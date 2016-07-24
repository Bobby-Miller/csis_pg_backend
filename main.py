from config.config import Configs
from pg_data.segments import Segment
from pg_data.stats import Stats
from ms_data.csis_status import CSISStatus
from pg_data.summary import Summary
from ms_data.csis_sql_orm import Session as MSSession
from pg_data.csis_pg_orm import PGSession
from db_data import DBData
from time import sleep
from threading import Thread, Lock
from sqlalchemy.exc import DBAPIError


class Main(Configs):
    def __init__(self):
        super().__init__()

        # Initialize helper objects
        self.segment = Segment()
        self.status = CSISStatus()

        # Gather batch data for comparison
        self.sorted_segment_set = self.segment.sorted_segments()
        self.db_data = DBData()

        # Adding report data to DB
        for batch in self.sorted_segment_set:
            self.db_data.update_summary_and_stats(batch)
            self.db_data.commit()

        # Initialize current batch data
        self.current_segment = self.segment.current_segment()

        # Initialize thread and locks
        self.thread_lock = Lock()

        # Track summary changes
        self.summary = Summary(self.current_segment)
        self.summary_time = self.summary.misc_data()['time']
        self.current_inspected = self.summary.data().inspected

    def summary_changed(self):
        self.current_segment = self.segment.current_segment()
        self.summary = Summary(self.current_segment)
        summary_time_check = self.summary.misc_data()['time']
        inspected_check = self.summary.data().inspected
        if self.summary_time == summary_time_check and self.current_inspected == inspected_check:
            return False
        else:
            self.summary_time = summary_time_check
            self.current_inspected = inspected_check
            return True

    def status_loop(self):
        while True:
            try:
                self.status.reset_session()
                sleep(self.configs['status_timer'])
                data_compare = self.status.compare_status_w_file()
                if data_compare:
                    pass
                else:
                    with self.thread_lock:
                        self.status.update_db_status()
            except DBAPIError:
                pass

    def report_loop(self):
        while True:
            try:
                self.db_data.reset_session()
                sleep(self.configs['report_timer'])
                last_batch = self.current_segment
                if self.summary_changed():
                    self.db_data.update_summary_and_stats(self.current_segment)
                with self.thread_lock:
                    self.db_data.commit()
            except DBAPIError:
                pass


if __name__ == '__main__':
    main = Main()
    status_task = Thread(target=main.status_loop)
    batch_task = Thread(target=main.report_loop)
    status_task.start()
    batch_task.start()
