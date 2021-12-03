## AG: Adopted from some boilerplate I developed in my CS6400 project
import pandas as pd
import sqlalchemy as sqla
import sqlalchemy.orm as orm
import traceback

class TableHandle(object):
    def __init__(self, table):
        self.table = table
        self.c = table.c

    @property
    def select(self):
        return sqla.select(self.table)

    @property
    def update(self):
        return sqla.update(self.table)

    @property
    def insert(self):
        return sqla.insert(self.table)

    @property
    def delete(self):
        return sqla.delete(self.table)

class Database(object):

    def __init__(self, url, *, tables=None, future=True, **kwargs):
        self.url = url
        self.engine = sqla.create_engine(url, future=future, **kwargs)
        self.session = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                future=future
            )
        )
        self.meta = sqla.MetaData(self.engine)
        self._load_tables = [] if tables is None else tables
        self._tables = {}

    def __getitem__(self, table):
        """
        Gets requested table name
        """
        if table not in self._tables:
            raise NameError("No such table '{}'".format(table))
        return TableHandle(self._tables[table])

    # def add_teardown(self, app):
    #
    #     @app.teardown_appcontext
    #     def kill_session(exception=None):
    #         self.session.remove()
    #
    #     return kill_session

    def commit(self):
        """
        Commits Changes
        """
        self.session.commit()

    def query(self, query, **kwargs):
        """
        Execute the given query
        """
        if isinstance(query, str):
            query = sqla.text(query)
        return pd.read_sql(query, self.session.connection(), params=kwargs if len(kwargs) else None)

    def insert(self, table, **values):
        return self.session.execute(self[table].insert, values)

    def multi_insert(self, table, values):
        if not len(values):
            return
        return self.session.execute(self[table].insert, values)

    def execute(self, statement):
        return self.session.execute(statement)

    def load_table(self, table_name):
        table = sqla.Table(
            table_name,
            self.meta,
            autoload_with=self.engine
        )
        self._tables[table_name] = table
        return table

    def load_tables(self, *table_names):
        tables = [
            sqla.Table(
                name,
                self.meta,
                autoload_with=self.engine
            )
            for name in table_names
        ]
        for name, table in zip(table_names, tables):
            self._tables[name] = table
        return tables

    def read_table(self, table_name):
        """
        Return the requested table in full
        """
        return self.query(
            self[table_name].select
        )

    def __enter__(self):
        self.load_tables(*self._load_tables)
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if (exc_type is not None or exc_val is not None or tb is not None):
            traceback.print_exc()
            # self.abort()
        else:
            self.commit()
