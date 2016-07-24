import csv
from csis_sql_orm import Session, CSISCurrent
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from config.config import Configs


class CSISStatus(Configs):
    def __init__(self):
        # Pull in config class variables
        super().__init__()
        # Initialize DB/ORM session for use in class
        self.session = Session()
        # Pull status from db, if exists.
        try:
            self.db_status = self.session.query(CSISCurrent).filter_by(id=1).one()
        except NoResultFound:
            self.db_status = None
        except MultipleResultsFound:
            print('multiple results found')
            try:
                self.session.query(CSISCurrent).delete()
                self.session.commit()
            except:
                self.session.rollback()

        self.status_list = self.status_from_file()

    @property
    def db_status(self):
        return self.__db_status

    @db_status.setter
    def db_status(self, db_status):
        """
        Sets db_status to what is in the file if the database, and adds the file data to
        the database if None.
        :param db_status: namedtuple: status data set.
        :return: No return
        """
        if db_status is None:
            # self.db_status = CSISCurrent(self.status_from_file())
            # self.session.add(self.db_status)
            status_dict = self.status_from_file()
            sql_labels = {
                'batch_id': status_dict["batch_id"], 'total': status_dict["Total"],
                'passed': status_dict["Pass"], 'failed': status_dict["Fail"],
                'failed_od': status_dict["Fail OD"],
                'backwards': status_dict["Backwards"], 'n_a': status_dict["N/A"],
                'lost_homing': status_dict[" Lost to Homing"],
                'batch_homes': status_dict["Batch Homes"],
            }
            self.__db_status = CSISCurrent(id=1, **sql_labels)
            self.session.add(self.__db_status)
            self.session.commit()
        else:
            self.__db_status = db_status

    @property
    def status_list(self):
        return self.__status_list

    @status_list.setter
    def status_list(self, status_list):
        if status_list is None:
            self.__status_list = self.status_from_file()
        else:
            self.__status_list = status_list

    def status_from_file(self):
        """
        Pull status data from the file, and return a dict whose key is the data title,
        and whose value is converted to int, or float, or string in that order, based
        on convertability
        :return: status list
        """
        data_path = self.data_path + '/Status.txt'
        with open(data_path, 'r') as file_data:
            reader = csv.reader(file_data, delimiter=':')
            status_dict = {}
            status_dict['batch_id'] = next(reader)[1][1:]
            for data in reader:
                try:
                    status_dict[data[0]] = int(data[1])
                except ValueError:
                    try:
                        status_dict[data[0]] = float(data[1])
                    except ValueError:
                        status_dict[data[0]] = data[1]
            return status_dict

    def compare_status_w_file(self):
        file = self.status_from_file()
        if file == self.status_list:
            return True
        else:
            self.status_list = file
            return False

    def update_db_status(self):
        self.db_status.batch_id = self.status_list['batch_id']
        self.db_status.total = self.status_list['Total']
        self.db_status.passed = self.status_list['Pass']
        self.db_status.failed = self.status_list['Fail']
        self.db_status.failed_od = self.status_list['Fail OD']
        self.db_status.backwards = self.status_list['Backwards']
        self.db_status.n_a = self.status_list['N/A']
        self.db_status.lost_homing = self.status_list[' Lost to Homing']
        self.db_status.batch_homes = self.status_list['Batch Homes']
        self.session.add(self.db_status)
        self.session.commit()

    def reset_session(self):
        self.session.close()
        self.session = Session()

if __name__ == '__main__':
    CSISStatus().update_db_status()
