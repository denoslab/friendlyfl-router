def sort_runs(runs):
    merged_runs = {}

    for run in runs:
        batch = run['batch']
        if batch not in merged_runs:
            merged_runs[batch] = run
        else:
            merged_runs[batch] = update_run(merged_runs[batch], run)
    sorted_dict = dict(sorted(merged_runs.items(), key=lambda x: x[0]))
    return list(sorted_dict.values())


def update_run(run_old, run_new):
    create_at = "created_at"
    update_at = "updated_at"
    status = "status"

    create_at_cur = run_old[create_at]
    update_at_cur = run_old[update_at]
    status_cur = run_old[status]

    create_at_new = run_new[create_at]
    update_at_new = run_new[update_at]
    status_new = run_new[status]

    if create_at_new < create_at_cur:
        run_old[create_at] = create_at_new
    if update_at_new > update_at_cur:
        run_old[update_at] = update_at_new
    if status_new < status_cur:
        run_old[status] = status_new
    return run_old
