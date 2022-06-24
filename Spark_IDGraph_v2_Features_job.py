# Databricks notebook source
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

#%run /Users/eh163e@att.com/utl/set_service_principal

import os
storage_account_name = 'famlisandbox'
account_key = 'VfoVtpIVrX/oWho1rgH8T1Enp2498baAtPFzAyu2Ov6IVoLK0mw1fwZv/acgXlP4p01RS+eFyPm4fFrmTahMkA=='
os.environ['AZURE_ACCOUNT_NAME'] = storage_account_name
os.environ['AZURE_ACCOUNT_KEY']= account_key

spark.conf.set("fs.azure.account.auth.type.famlisandbox.dfs.core.windows.net", "OAuth")
spark.conf.set("fs.azure.account.oauth.provider.type.famlisandbox.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set("fs.azure.account.oauth2.client.id.famlisandbox.dfs.core.windows.net", "6f41f6a6-b08c-4aac-9a6c-dde6e60da73c")
#spark.conf.set("fs.azure.account.oauth2.client.secret.famlisandbox.dfs.core.windows.net", dbutils.secrets.get(scope="eh163e_kv",key="famlispgeneral"))
spark.conf.set("fs.azure.account.oauth2.client.secret.famlisandbox.dfs.core.windows.net", dbutils.secrets.get(scope="AzureProdKeyVault-2",key="famlisandbox-sp-client-id"))
spark.conf.set("fs.azure.account.oauth2.client.endpoint.famlisandbox.dfs.core.windows.net", "https://login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/token")
print("Your service principal is set!")

# COMMAND ----------

fromDate = str(dbutils.widgets.get("date0"))
toDate = str(dbutils.widgets.get("date2"))
date1 = str(dbutils.widgets.get("date1"))
date2 = str(dbutils.widgets.get("date2"))

READ_PATH = f"abfss://passthrough@raicnprdpassthrough.dfs.core.windows.net/identity_graph_v2/updated_data/"

print("Starting Job")
print(f"Cache data between {fromDate} and {toDate}")
print(f"Create features for {date1} to {date2}")

# COMMAND ----------

# MAGIC %md
# MAGIC # Read in Dataframes

# COMMAND ----------

# MAGIC %md
# MAGIC # Features

# COMMAND ----------

base_path = "abfss://famli-dev-workspace@famlisandbox.dfs.core.windows.net/eh163e/data/robocalling/identity_graph_v2/"

#read out source tables
# cache all tables since we will be looping over dates to generate features and caching data will be faster
commonIDtoWirelessBAN = spark.read.format('delta').load(base_path+"commonIDtoWirelessBAN").cache()
WirelessBANtoIPaddress= spark.read.format('delta').load(base_path+"WirelessBANtoIPaddress").cache()
WirelessBANtoAddress= spark.read.format('delta').load(base_path+"WirelessBANtoAddress").cache()
WirelessBANtoEmail= spark.read.format('delta').load(base_path+"WirelessBANtoEmail").cache()
Transaction= spark.read.format('delta').load(base_path+"Transaction").drop("data_dt").cache()

# COMMAND ----------

# # set on cluster
# # spark.databricks.session.share to true
# # setup shared cache tables
# commonIDtoWirelessBAN.createOrReplaceGlobalTempView("commonIDtoWirelessBAN")
# WirelessBANtoIPaddress.createOrReplaceGlobalTempView("WirelessBANtoIPaddress")
# WirelessBANtoAddress.createOrReplaceGlobalTempView("WirelessBANtoAddress")
# WirelessBANtoEmail.createOrReplaceGlobalTempView("WirelessBANtoEmail")
# Transaction.createOrReplaceGlobalTempView("Transaction")

# # on second notebooks
# global_temp_db = spark.conf.get("spark.sql.globalTempDatabase")
# commonIDtoWirelessBAN= table(global_temp_db + ".commonIDtoWirelessBAN")
# WirelessBANtoIPaddress= table(global_temp_db + ".WirelessBANtoIPaddress")
# WirelessBANtoAddress= table(global_temp_db + ".WirelessBANtoAddress")
# WirelessBANtoEmail= table(global_temp_db + ".WirelessBANtoEmail")
# Transaction= table(global_temp_db + ".Transaction")

# COMMAND ----------

from delta.tables import *
from pyspark.sql.functions import *

#delete unfinished partitions
output_path = "abfss://famli-dev-workspace@famlisandbox.dfs.core.windows.net/eh163e/data/robocalling/identity_graph_v2/features_iter1_spark_export"
deltaTable = DeltaTable.forPath(spark, output_path)
#deltaTable.delete("data_dt == '2021-06-13'")

# COMMAND ----------

output_path = "abfss://famli-dev-workspace@famlisandbox.dfs.core.windows.net/eh163e/data/robocalling/identity_graph_v2/features_iter1_spark_export"
from datetime import datetime, timedelta 
#dates = ["2021-05-02","2021-05-03","2021-05-04","2021-05-05","2021-05-06","2021-05-07"]#"2021-05-01"]#,
ouput_cols = ['wirelessban','channel','runlevel','FeatureValue','data_dt','period','FeatureName']

import pandas as pd
# date1 = '20210613'
# date2 = '20220301'
dates = [str(dt.date()) for dt in pd.date_range(date1, date2).tolist()]

for data_dt in dates:
  print("running:",data_dt)
  start=datetime.now()
  
  # maybe reduce input data for last 30 days to be able to broadcast commonIDtoWirelessBAN as well, which is > 10GB causing maxResultSize Error
  
  for i in [1,3,7,14,30]:
    dt_lb = str((datetime.strptime(data_dt,"%Y-%m-%d").date() - timedelta(days=i)))

    # EMAIL
    (Transaction.drop("data_dt")
       #first hop
      .join(commonIDtoWirelessBAN.drop("data_dt"), on ="commonid")
      .join(broadcast(WirelessBANtoEmail.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="wirelessban")
      .withColumn("data_dt",to_date(col("applicationtimestamp")))
      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
      .groupBy("email","channel","runlevel")
      .agg(sum(col("sessionid_count")).alias("FeatureValue"))
       #second hop                  
      .join(broadcast(WirelessBANtoEmail.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="email")
      .groupBy("wirelessban","channel","runlevel")
      .agg(sum(col("FeatureValue")).alias("FeatureValue"))
      .withColumn("data_dt",lit(data_dt))
      .withColumn("period",lit(i))
      .withColumn("FeatureName",lit("velocityEmailTwoHop"))
      ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
  
    # IPAddress
    (Transaction
     #first hop
    .join(commonIDtoWirelessBAN.drop("data_dt"), on ="commonid")
    .join(broadcast(WirelessBANtoIPaddress.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="wirelessban")
    .withColumn("data_dt",to_date(col("applicationtimestamp")))
    .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
    .groupBy("ipaddress","channel","runlevel")
    .agg(sum(col("sessionid_count")).alias("FeatureValue"))
     #second hop                  
    .join(broadcast(WirelessBANtoIPaddress.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="ipaddress")
    .groupBy("wirelessban","channel","runlevel")
    .agg(sum(col("FeatureValue")).alias("FeatureValue"))
    .withColumn("data_dt",lit(data_dt))
    .withColumn("period",lit(i))
    .withColumn("FeatureName",lit("velocityIPAddressTwoHop"))
    ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
    
    #Address
    (Transaction
       #first hop
      .join(commonIDtoWirelessBAN.drop("data_dt"), on ="commonid")
      .join(broadcast(WirelessBANtoAddress.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="wirelessban")
      .withColumn("data_dt",to_date(col("applicationtimestamp")))
      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
      .groupBy("address","channel","runlevel")
      .agg(sum(col("sessionid_count")).alias("FeatureValue"))
       #second hop                  
      .join(broadcast(WirelessBANtoAddress.filter(f"data_dt between '{dt_lb}' and '{data_dt}'").drop("data_dt").distinct()), on ="address")
      .groupBy("wirelessban","channel","runlevel")
      .agg(sum(col("FeatureValue")).alias("FeatureValue"))
      .withColumn("data_dt",lit(data_dt))
      .withColumn("period",lit(i))
      .withColumn("FeatureName",lit("velocityAddressTwoHop"))
      ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
    
    #BAN
    (Transaction
    .join(commonIDtoWirelessBAN, on ="commonid")
    .withColumn("data_dt",to_date(col("applicationtimestamp")))
    .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
    .groupBy("wirelessban","channel","runlevel")
    .agg(sum(col("sessionid_count")).alias("FeatureValue"))
    .withColumn("data_dt",lit(data_dt))
   .withColumn("period",lit(i))
    .withColumn("FeatureName",lit("velocityBanOneHop"))
   ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)

    #velocityBanTwoHopEmail
    (WirelessBANtoEmail
      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
      .drop("data_dt")
      .join(broadcast(WirelessBANtoEmail
                      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
                      .drop("data_dt")
                      .withColumnRenamed("wirelessban","wirelessban2")), on="email")
      .filter(col("wirelessban")!=col("wirelessban2"))
      .drop("email").distinct().groupby("wirelessban").count()
      .withColumnRenamed("count","FeatureValue")
      .withColumn("FeatureName",lit("velocityBanTwoHopEmail"))
      .withColumn("channel",lit("omni"))
      .withColumn("runlevel",lit(0))
      .withColumn("data_dt",lit(data_dt))
      .withColumn("period",lit(i))
      ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
  
    #velocityBanTwoHopAddress
    (WirelessBANtoAddress
      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
      .drop("data_dt")
      .join(broadcast(WirelessBANtoAddress
                      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
                      .drop("data_dt")
                      .withColumnRenamed("wirelessban","wirelessban2")
                     ), on="address")
      .filter(col("wirelessban")!=col("wirelessban2"))
      .drop("address").distinct().groupby("wirelessban").count()
      .withColumnRenamed("count","FeatureValue")
      .withColumn("FeatureName",lit("velocityBanTwoHopAddress"))
      .withColumn("channel",lit("omni"))
      .withColumn("runlevel",lit(0))
      .withColumn("data_dt",lit(data_dt))
      .withColumn("period",lit(i))
      ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
  
    #velocityBanTwoHopIPAddress
    (WirelessBANtoIPaddress
      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
      .drop("data_dt")
      .join(broadcast(WirelessBANtoIPaddress
                      .filter(f"data_dt between '{dt_lb}' and '{data_dt}'")
                      .drop("data_dt")
                      .withColumnRenamed("wirelessban","wirelessban2")), on="ipaddress")
      .filter(col("wirelessban")!=col("wirelessban2"))
      .drop("ipaddress").distinct().groupby("wirelessban").count()
      .withColumnRenamed("count","FeatureValue")
      .withColumn("FeatureName",lit("velocityBanTwoHopIPAddress"))
      .withColumn("channel",lit("omni"))
      .withColumn("runlevel",lit(0))
      .withColumn("data_dt",lit(data_dt))
      .withColumn("period",lit(i))
      ).select(ouput_cols).write.partitionBy("data_dt").format('delta').mode('append').save(output_path)
  #get run
  difference = datetime.now() - start
  seconds_in_day = 24 * 60 * 60
  total_seconds = difference.days * seconds_in_day + difference.seconds
  time_diff = divmod(total_seconds, 60)
  runtime = str(time_diff[0])+"m "+str(time_diff[1])+"s"
  print("runtime:",runtime)
