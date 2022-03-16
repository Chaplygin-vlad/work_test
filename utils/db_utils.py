import psycopg2

from auth import DB_PARAMS
from utils.logger import LogDispatcher


class PgSession:
    """Класс для открытия сессии подключения к БД"""

    def __init__(self):
        self.host = DB_PARAMS['host']
        self.db = DB_PARAMS['db']
        self.port = DB_PARAMS['port']
        self.user = DB_PARAMS['user']
        self.password = DB_PARAMS['password']
        self.logger = LogDispatcher().log

    def __enter__(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                dbname=self.db,
                port=self.port,
                user=self.user,
                password=self.password
            )
            self.logger.info('Подключено к БД')
        except psycopg2.OperationalError as e:
            self.logger.error('Ошибка подключения к БД')

            raise e

        else:
            return self.connection

    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


class CrudDatabase:
    """Класс для работы с БД"""

    def __init__(self):
        self.logger = LogDispatcher().log

    def update_end_expiration_devices(self):
        """Метод для обновления поля active у устройств с истекшим exp_date"""
        with PgSession() as connection:
            cursor = connection.cursor()
            query = '''
            UPDATE public.devices
            SET active=FALSE 
            FROM (
            SELECT id, profile_id, exp_date
            FROM public.devices
            WHERE active=TRUE AND exp_date < current_timestamp              
                  ) as ending_dev
            WHERE public.devices.id = ending_dev.id
            RETURNING public.devices.id;                
            '''
            cursor.execute(query)
            exp_devices = cursor.fetchall()  # id возвращаются для логов
            self.logger.info(
                f'{len(exp_devices)} устройств помечены неактивными по причине окончания срока действия')

    def delete_null_instance_devices(self):
        """Метод для удаления устройств с истекшим сроком действия и пустым или равным Null instance_id"""
        with PgSession() as connection:
            cursor = connection.cursor()
            query = '''
            DELETE FROM public.devices 
            WHERE instance_id is null or instance_id = '' and exp_date < current_timestamp
            RETURNING public.devices.id
            '''
            cursor.execute(query)
            null_devices = cursor.fetchall()  # id возвращаются для логов
            self.logger.info(f'Удалено {len(null_devices)} устройств с пустым instance_id')

    def filter_double_devices(self):
        """Метод для пометки дублей устройств каждого профиля как неактивные, кроме максимального по сроку действия"""
        with PgSession() as connection:
            cursor = connection.cursor()
            query = """
            UPDATE devices
            SET active = false
            FROM (
            SELECT *
            FROM devices as d_1
            WHERE active = TRUE
            AND exp_date <> (SELECT MAX(exp_date) FROM devices as d_2
            WHERE active = TRUE AND d_1.instance_id = d_2.instance_id AND d_1.profile_id= d_2.profile_id)) AS tmp
            WHERE devices.id = tmp.id
            RETURNING devices.id
            """
            cursor.execute(query)
            double_devices = cursor.fetchall()  # id возвращаются для логов
            self.logger.info(f'{len(double_devices)} дублирующих устройств помечены неактивными')
