from utils.db_utils import CrudDatabase


def check_and_update_db():
    """Метод для проверки и обновления базы данных на предмет дублей и истекших записей устройств"""

    crud_database = CrudDatabase()
    crud_database.delete_null_instance_devices()
    crud_database.update_end_expiration_devices()
    crud_database.filter_double_devices()
