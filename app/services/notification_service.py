import logging

logger = logging.getLogger(__name__)

# TODO Phase 3: FCM/APNs push notification integration.
# Replace logger calls with real FCM/APNs API requests.
# Device tokens are stored in the device_tokens table.
# All notification triggers must go through this module — never inline in routers.


async def notify_issue_status_changed(
    issue_id: str, old_status: str, new_status: str
) -> None:
    logger.info(
        "[NOTIFY] Issue %s status changed: %s -> %s", issue_id, old_status, new_status
    )


async def notify_new_announcement(announcement_id: str, complex_id: str) -> None:
    logger.info(
        "[NOTIFY] New announcement %s for complex %s", announcement_id, complex_id
    )
