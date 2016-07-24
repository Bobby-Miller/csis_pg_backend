from csis_pg_orm import Batch, TestPass, MeasurementMean, MeasurementCount, PGSummary, \
    PGSession
from summary import Summary
from stats import Stats
from collections import namedtuple
from sqlalchemy.exc import IntegrityError
from psycopg2 import IntegrityError as psycoIntegrityError


class DBData:
    def __init__(self):
        self.session = PGSession()
        self.db_batches = self.batches_from_db()

    def batches_from_db(self):
        """
        Collect the batch data sets entered in the database. Use as reference
        against existing folders.
        :return: set of batch lists
        """
        batch_data = set()
        Point = namedtuple('db_batch', 'batch_name')
        for name in self.session.query(Batch.batch_id):
            batch_data.add(Point(name))
        return batch_data

    def add_batch(self, batch: namedtuple) -> None:
        """
        Adds a batch to the db session from a batch namedtuple
        :param batch: (namedtuple) batch details
        :return: No return
        """
        try:
            batch_line = Batch(batch_id=batch.batch_name)
            print(batch_line)
            self.session.add(batch_line)
            self.session.commit()
        except IntegrityError:
            self.reset_session()
        except psycoIntegrityError:
            self.reset_session()

    def update_summary(self, batch: namedtuple):
        """
        Add batch, then add or update summary in DB
        :param batch:
        :return:
        """
        self.add_batch(batch)
        summary = Summary(batch)
        if summary.exists():
            summary_data = summary.data()
            summary_info = summary.misc_data()
            batch_id = batch.batch_name
            summary_line = (self.session
                            .query(PGSummary)
                            .filter_by(
                                batch_id=batch_id,
                                date=summary_info['date'],
                                time=summary_info['time']
                            )
                            .one_or_none())
            if summary_line:
                for key, val in summary_data._asdict().items():
                    setattr(summary_line, key, val)
                summary_line.gate_homes = summary_info['gate_homes']
                summary_line.lost_homing = summary_info['lost_homing']
            else:
                summary_line = PGSummary(
                    batch_id=batch_id, **summary_data._asdict(), **summary_info
                )
                self.session.add(summary_line)
            self.session.flush()
            return summary_line

    def update_summary_and_stats(self, batch: namedtuple) -> None:
        """
        Add batch, then add or update summary, and finally add or update stats
        :param batch:
        :return:
        """
        stats = Stats(batch)
        if stats.exists():
            with self.session.no_autoflush:
                summary = self.update_summary(batch)
                stats_dict = stats.group_count_average()
                batch_id = batch.batch_name

                def update_or_add(group, model, dictionary):
                    instance = (self.session.query(model)
                                .filter_by(
                                    batch_id=batch_id,
                                    summary_id=summary.id,
                                    overall_result=group
                                )
                                .one_or_none())

                    if instance:
                        for key, val in dictionary.items():
                            setattr(instance, key, val)
                    else:
                        instance = model(
                            batch_id=batch_id,
                            summary_id=summary.id,
                            overall_result=group,
                            **dictionary
                        )
                        self.session.add(instance)

                model_list = [TestPass, MeasurementMean, MeasurementCount]

                for group, group_dict in stats_dict.items():
                    dict_list = [
                        group_dict['tests'],
                        group_dict['measurements']['averages'],
                        group_dict['measurements']['counts'],
                    ]
                    for model, dictionary in zip(model_list, dict_list):
                        update_or_add(group, model, dictionary)

    def commit(self):
        self.session.commit()

    def reset_session(self):
        self.session.close()
        self.session = PGSession()

if __name__ == '__main__':
    test_obj = DBData()
    print(test_obj.batches_from_db())

