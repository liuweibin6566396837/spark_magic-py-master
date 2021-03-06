# -*- encoding: utf-8 -*-
# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
# The class MUST call this class decorator at creation time
import sys

import findspark

findspark.init("/usr/hdp/current/spark2/")  # 这个args要指明SPARK_HOME 例如:findspark.init("/usr/hdp/2.6.2.0-205/spark2/")
from pyspark.sql import SparkSession
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)

PYTHON_PATH = sys.executable  # 当前使用python环境路径


@magics_class
class SparkMagics(Magics):
    @line_magic
    def lmagic(self, line):
        "my line magic"
        print("Full access to the main IPython object:", self.shell)
        print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        return line

    @cell_magic
    def cmagic(self, line, cell):
        "my cell magic"
        return line, cell

    @line_cell_magic
    def pyspark(self, line, cell=None):
        "Magic that works both as %lcmagic and as %%lcmagic"
        if cell is None:
            print("Called as line magic")
            spark = SparkSession.builder.appName("jupyter-shell") \
                .config("spark.master", "yarn") \
                .config("spark.submit.deployMode", "client") \
                .config("spark.pyspark.python", PYTHON_PATH) \
                .config("spark.pyspark.driver.python", PYTHON_PATH) \
                .config("spark.driver.memory", "1g") \
                .config("spark.executor.memory", "1g") \
                .config("spark.executor.cores", "2") \
                .config("spark.executor.instances", "4") \
                .enableHiveSupport() \
                .getOrCreate()
            sc = spark.sparkContext
            return spark, sc
        else:
            print("Called as cell magic")
            properties = {}
            args = cell.split()
            for arg in args:
                properties[arg.split(":")[0]] = arg.split(":")[1]

            # 判断一些基本配置是否存在, 设置默认配置
            if "spark.submit.deployMode" not in properties.keys():
                properties["spark.submit.deployMode"] = "client"  # 默认使用client模式
            if "spark.app.name" not in properties.keys():
                properties["spark.app.name"] = "jupyter-shell"
            if "spark.pyspark.driver.python" not in properties.keys():
                properties["spark.pyspark.driver.python"] = PYTHON_PATH
            if "spark.pyspark.python" not in properties.keys():
                properties["spark.pyspark.python"] = PYTHON_PATH
            if "spark.driver.memory" not in properties.keys():
                properties["spark.driver.memory"] = "2g"
            if "spark.executor.memory" not in properties.keys():
                properties["spark.executor.memory"] = "2g"
            if "spark.executor.cores" not in properties.keys():
                properties["spark.executor.cores"] = "1"
            if "spark.executor.instances" not in properties.keys():
                properties["spark.executor.instances"] = "2"
            if "spark.yarn.dist.archive" not in properties.keys():  # 上传依赖包：本地或hdfs
                properties["spark.yarn.dist.archive"] = None
            if "spark.yarn.appMasterEnv.PYSPARK_PYTHON" not in properties.keys():
                properties["spark.yarn.appMasterEnv.PYSPARK_PYTHON"] = None
            if "spark.executorEnv.PYSPARK_PYTHON" not in properties.keys():
                properties["spark.executorEnv.PYSPARK_PYTHON"] = None
            if "spark.hive.cluster" not in properties.keys():
                properties["spark.hive.cluster"] = "local_cluster"
                properties["hive.metastore.uris"] = None
            elif properties["spark.hive.cluster"] == "offline_cluster":
                properties["hive.metastore.uris"] = "thrift://10.5.145.113:9083"
            if "spark.pyspark.virtualenv.enabled" not in properties.keys():
                properties["spark.pyspark.virtualenv.enabled"] = "false"
            if "spark.pyspark.virtualenv.type" not in properties.keys():
                properties["spark.pyspark.virtualenv.type"] = None
            if "spark.pyspark.virtualenv.requirements" not in properties.keys():
                properties["spark.pyspark.virtualenv.requirements"] = None
            if "spark.pyspark.virtualenv.bin.path" not in properties.keys():
                properties["spark.pyspark.virtualenv.bin.path"] = None

            spark = SparkSession \
                .builder \
                .config("spark.app.name", properties["spark.app.name"]) \
                .config("spark.master", "yarn") \
                .config("spark.submit.deployMode", properties["spark.submit.deployMode"]) \
                .config("spark.pyspark.virtualenv.enabled", properties["spark.pyspark.virtualenv.enabled"]) \
                .config("spark.pyspark.virtualenv.type", properties["spark.pyspark.virtualenv.type"]) \
                .config("spark.pyspark.virtualenv.requirements", properties["spark.pyspark.virtualenv.requirements"]) \
                .config("spark.pyspark.virtualenv.bin.path", properties["spark.pyspark.virtualenv.bin.path"]) \
                .config("spark.yarn.dist.archive", properties["spark.yarn.dist.archive"]) \
                .config("spark.yarn.appMasterEnv.PYSPARK_PYTHON", properties["spark.yarn.appMasterEnv.PYSPARK_PYTHON"]) \
                .config("spark.executorEnv.PYSPARK_PYTHON", properties["spark.executorEnv.PYSPARK_PYTHON"]) \
                .config("spark.pyspark.driver.python", properties["spark.pyspark.driver.python"]) \
                .config("spark.pyspark.python", properties["spark.pyspark.python"]) \
                .config("spark.driver.memory", properties["spark.driver.memory"]) \
                .config("spark.executor.memory", properties["spark.executor.memory"]) \
                .config("spark.executor.cores", properties["spark.executor.cores"]) \
                .config("spark.executor.instances", properties["spark.executor.instances"]) \
                .config("hive.metastore.uris", properties["hive.metastore.uris"]) \
                .enableHiveSupport() \
                .getOrCreate()
            sc = spark.sparkContext
            if properties["spark.hive.cluster"] == "offline_cluster":
                sc._jsc.hadoopConfiguration().set("fs.defaultFS", "hdfs://umecluster")
                sc._jsc.hadoopConfiguration().set("dfs.nameservices", "umecluster")
                sc._jsc.hadoopConfiguration().set("dfs.ha.namenodes.umecluster", "nn1,nn2")
                sc._jsc.hadoopConfiguration().set("dfs.namenode.rpc-address.umecluster.nn1",
                                                  "hdfs://10.5.145.109:8020")
                sc._jsc.hadoopConfiguration().set("dfs.namenode.rpc-address.umecluster.nn2",
                                                  "hdfs://10.5.145.110:8020")
                sc._jsc.hadoopConfiguration().set("dfs.client.failover.proxy.provider.umecluster",
                                                  "org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider")
            return spark, sc


# In order to actually use these magics, you must register them with a
# running IPython.

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(SparkMagics)


ipy = get_ipython()
ipy.register_magics(SparkMagics)
