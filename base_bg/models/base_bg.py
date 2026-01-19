##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import json
import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any

from odoo import _, api, models

if TYPE_CHECKING:
    from base_bg.models.bg_job import BgJob


class BaseBg(models.AbstractModel):
    _name = "base.bg"
    _description = "Background Job Mixin"

    @api.model
    def bg_enqueue_records(
        self, records: models.BaseModel, method: str, threshold: int | None = None, *args, **kwargs
    ) -> tuple[dict, "BgJob"]:
        """
        Enqueue background jobs in batches based on record threshold.

        This is a model/API method and must be called on the model, passing
        the target records as the first argument. Example:
            self.env['base.bg'].bg_enqueue_records(records, 'method_name', threshold=..., ...)

        :param records: recordset to process; can be empty for no specific targets
        :param method: The method name to execute on each batch
        :param threshold: Maximum number of records per job
        :param args: Positional arguments for the method
        :param kwargs: Keyword arguments for the method
            Special kwargs:
                :param priority: Job priority (default: 10)
                :param max_retries: Maximum retries for the job (default: 3)
                :param name: Base name for the job(s) (default: model.method-uuid)
        :return: A display notification and the created jobs
        """
        # Normalize records into ids; allow None/empty to mean no targets
        jobs = self.env["bg.job"]
        model = records._name
        record_ids = records.ids if records else []
        context = self.make_serializable(dict(self.env.context), filter_unserializable=True)
        priority = max(kwargs.pop("priority", 10), 0)
        max_retries = kwargs.pop("max_retries", 3)
        name = kwargs.pop("name", "")

        def _get_name(batch_key: str, queue_order: int) -> str:
            return name or "%s.%s-%s-%s" % (model, method, batch_key[0:8], queue_order)

        batch_key = str(uuid.uuid4())
        total = len(record_ids) or 1  # Ensure at least one job if no records
        threshold = max(1, threshold or total)
        prev_job = None
        for i in range(0, total, threshold):
            chunk_ids = record_ids[i : i + threshold]
            queue_order = i // threshold
            job_vals = {
                "name": _get_name(batch_key, queue_order),
                "model": model,
                "method": method,
                "priority": priority,
                "max_retries": max_retries,
                "context_json": context,
                "batch_key": batch_key,
                "state": "enqueued" if queue_order == 0 else "waiting",
            }
            job_kwargs = kwargs.copy() or {}
            job_kwargs["_record_ids"] = list(chunk_ids) if chunk_ids else []
            job_vals["args_json"] = self.make_serializable(list(args)) if args else []
            job_vals["kwargs_json"] = self.make_serializable(job_kwargs)
            job = self.env["bg.job"].create(job_vals)
            jobs |= job
            # Link previous job to current so sequence is established in one pass
            if prev_job:
                prev_job.next_job_id = job.id
            prev_job = job

        self.sudo()._trigger_crons()
        title = _("Processes sent to background successfully")
        message = _("You will be notified when they are done.")
        return (
            {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": title,
                    "type": "success",
                    "message": message,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            },
            jobs,
        )

    def bg_enqueue(self, method: str, threshold: int | None = None, *args, **kwargs) -> tuple[dict, "BgJob"]:
        """
        Instance-style enqueuing helper.

        Usage:
            _inherit = ['base.bg', ...]
            ...
            records.bg_enqueue('method_name', threshold=..., ...)

        Delegates to the model API `bg_enqueue_records` using the calling recordset as the `records` parameter.
        """
        return self.bg_enqueue_records(self, method, threshold, *args, **kwargs)

    def _trigger_crons(self):
        """
        Trigger cron jobs to process enqueued background jobs
        """
        code = "_cron_run_enqueued_jobs("
        crons = self.env["ir.cron"].search([("code", "ilike", code)])
        for cron in crons:
            cron._trigger()

    @api.model
    def is_serializable(self, value: Any) -> bool:
        """
        Checks if a value is JSON serializable.

        :param value: The value to check
        :return: True if serializable, False otherwise
        """
        try:
            json.dumps(value)
            return True
        except Exception:
            return False

    @api.model
    def make_serializable(self, obj: Any, filter_unserializable: bool = False) -> Any:
        """
        Recursively make an object JSON serializable.

        Special handling:
        - Recordsets (BaseModel instances): convert to list of IDs
        - datetime objects: convert to ISO format string
        - For dicts: if filter_unserializable, omit keys with non-serializable values; else raise error.
        - For lists/tuples: if filter_unserializable, filter out non-serializable items; else raise error.
        - For other types: return the object if serializable, else raise ValueError if not filter_unserializable.

        :param obj: The object to make serializable
        :param filter_unserializable: If True, filter out non-serializable items instead
        :return: A JSON serializable version of the object
        """
        if isinstance(obj, models.BaseModel):
            return obj.ids
        elif isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {
                k: self.make_serializable(v, filter_unserializable) for k, v in obj.items() if self.is_serializable(v)
            }
        elif isinstance(obj, (list, tuple)):
            return [self.make_serializable(item, filter_unserializable) for item in obj]
        else:
            if not self.is_serializable(obj):
                if filter_unserializable:
                    return None
                raise ValueError(f"Object of type {type(obj).__name__} is not JSON serializable: {repr(obj)}")
            return obj
