from .models import Status

NATIVE_GATES = ("cargo_check", "cargo_test", "cargo_fmt", "cargo_clippy", "miri")

def aggregate_required(statuses):
    values = [Status(s) for s in statuses]
    if not values:
        return Status.VERIFIED
    return max(values, key=lambda s: {Status.VERIFIED:0, Status.PARTIALLY_VERIFIED:1, Status.PROVISIONAL:2, Status.BLOCKED:3}[s])
