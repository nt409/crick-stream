from functions import generate_scorecard_once, generate_scorecard_all_day
from config import config


def main(conf):
    if not conf["all_day"]:
        generate_scorecard_once(conf["url"],
                conf["sleep_time"],
                scorecard_every_n_overs=conf["show_full_sc_interval"],
                max_time_full_scorecard=conf["max_time_full_scorecard"])
    else:
        generate_scorecard_all_day(conf["url"],
                conf["sleep_time"],
                scorecard_every_n_overs=conf["show_full_sc_interval"],
                max_time_full_scorecard=conf["max_time_full_scorecard"])


if __name__=="__main__":
    main(config)
