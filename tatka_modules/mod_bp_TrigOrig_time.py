import numpy as np
from bp_types import Pick


def _time_average(times):
    try:
        ref_time = times[0]
    except IndexError:
        return None
    times = np.array([time - ref_time for time in times])
    return ref_time + times.mean()


#TODO: _time_stdev():


def TrOrig_time(config, stations, GRD_sta, trigger, arrival_times):

    dt_min = config.dt_min
    picks = []

    for sta, wave in ((sta, wave) for wave in config.wave_type for sta in stations):
        pick = Pick()
        pick.station = sta
        pick.arrival_type = wave
        pick.travel_time = GRD_sta[sta][wave].get_value(trigger.x, trigger.y, trigger.z)
        pick.pick_time = _time_average(arrival_times[sta][wave])
        picks.append(pick)

    # initial estimation of origin time
    bp_origin_time = _time_average([pick.pick_time - pick.travel_time for pick in picks])

    recalc_orig_time = False
    for pick in picks:
        pick.theor_time = bp_origin_time + pick.travel_time
        pick.time_dev = abs(pick.pick_time - pick.theor_time)
        if pick.time_dev >= dt_min :
            recalc_orig_time = True

    # recalculate origin time by disregarding picks with time_dev > dt_min
    if recalc_orig_time:
        bp_origin_time = _time_average([pick.pick_time - pick.travel_time
                                        for pick in picks if pick.time_dev < dt_min])
        if bp_origin_time is None:
            return
        for pick in picks:
            pick.theor_time = bp_origin_time + pick.travel_time

    trigger.origin_time = bp_origin_time
    trigger.eventid = trigger.origin_time.strftime("%Y%m%d_%H%M") + 'A'
    for pick in picks:
        pick.eventid = trigger.eventid
        # recompute pick_time and theor_time respect to origin_time
        pick.pick_time -= trigger.origin_time
        pick.theor_time -= trigger.origin_time
        trigger.add_pick(pick)

    if config.grid_type != config.wave_type:
        phase2 = list(set(config.grid_type)-set(config.wave_type))[0]
    # additional theoretical travel time estimation for second phase
    # only done if config.grid_type and config.wave_type have different number of phases
        for sta in stations:
            pick = Pick()
            pick.eventid = trigger.eventid
            pick.station = sta
            pick.arrival_type = phase2
            pick.theor_time = GRD_sta[sta][phase2].get_value(trigger.x, trigger.y, trigger.z)
            pick.pick_time = GRD_sta[sta][phase2].get_value(trigger.x, trigger.y, trigger.z)
            picks.append(pick)
            trigger.add_pick(pick)        
