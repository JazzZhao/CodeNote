import pymysql
import pandas as pd
from config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_PORT
)
fmt = "\n=== {:30} ===\n"

class Mysql:
    def __init__(self):
        print(fmt.format("start connecting to Mysql"))
        self.connect = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
    def get_question(self, company_id:str):
        #查询sql
        sql = """
            SELECT
            tsq.question_id question_id,
            tsq.question_name question_name,
            tsa.answer answer
            from
            (
            SELECT
            question_id,
            question_name
            FROM
            t_singledia_question tsq
            WHERE
            tsq.com_id = %s
            and status in (1, 2)) tsq
            LEFT JOIN (
            select
            question_id,
            answer
            from
            t_singledia_answer tsa
            WHERE
            tsa.com_id = %s
            and status = 1) tsa on
            tsa.question_id = tsq.question_id
            UNION
            SELECT
            tsq.question_id question_id,
            tsq.similar_question question_name,
            tsa.answer answer
            from
            (
            SELECT
            question_id,
            similar_question
            FROM
            t_similar_question tsq
            WHERE
            tsq.com_id = %s) tsq
            LEFT JOIN (
            select
            question_id,
            answer
            from
            t_singledia_answer tsa
            WHERE
            tsa.com_id = %s
            and status = 1) tsa on
            tsa.question_id = tsq.question_id
            """
        with self.connect.cursor() as cursor:
            cursor.execute(sql, (company_id,company_id,company_id,company_id))
            results = cursor.fetchall()
            # 处理查询结果
        return pd.DataFrame(results,    columns=['question_id','question', 'answer'])