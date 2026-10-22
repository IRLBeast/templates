в запросе остался кусок старой версии, и он обрывает структуру.
Почему именно такие ошибки
758/11 ORA-00903 указывает на строку FROM prm_dt_range, (10 пробелов, значит колонка 11). Она стоит сразу после LEFT OUTER JOIN и строки ----. После LEFT OUTER JOIN Oracle ждёт имя таблицы и видит FROM.
228/3 SQL statement ignored означает, что вставка INSERT INTO DWKR_02.REPORT_FS10_RESULT целиком не скомпилировалась из-за ошибки выше.
Что нужно исправить
Удалить обрывок. Блок от FROM prm_dt, (SELECT DISTINCT kd_act.* ... до LEFT OUTER JOIN ---- относится к старой версии (с kd_act, kd_act_crncy, prm_dt). Таких CTE у вас нет. Нужно вручную собрать kd_end_debt по образцу kd_begin_debt. Не хватает SELECT со списком полей и расчётом MAIN_DEBT_BYN из kd_end_flt_cr, kdf, kdis_byn, lt1_byn и остальных. Сейчас внешний SELECT с KD_TERM_MONTHS_GROUP не связан с подзапросами. Структура должна быть такой:
FROM (
  SELECT COALESCE(BASIS_ACTIVITY_ID,999) AS BASIS_ACTIVITY_ID, BANK_ID,
         KD_TERM_MONTHS_GROUP, SUM(MAIN_DEBT_BYN) AS MAIN_DEBT_BYN
  FROM (
    SELECT d.*,
           CASE ... MONTHS_BETWEEN(d.END_DATE_OSN+1, prm_dt_range.DATE_END) ... END AS KD_TERM_MONTHS_GROUP
    FROM prm_dt_range,
         ( SELECT ... FROM ... kd_end_flt_cr ... ) d          -- kd_end_debt
         LEFT OUTER JOIN ( SELECT ... ) kd_begin_debt
           ON kd_begin_debt.BORR_ID = d.BORR_ID AND kd_begin_debt.KRED_DOG_ID = d.KRED_DOG_ID
    WHERE COALESCE(kd_begin_debt.MAIN_DEBT_BYN,0) < COALESCE(d.MAIN_DEBT_BYN,0)
  )
  GROUP BY COALESCE(BASIS_ACTIVITY_ID,999), BANK_ID, KD_TERM_MONTHS_GROUP
) t2
Убрать ORDER BY kd_end_debt.BORR_ID... перед GROUP BY. Так ORDER BY стоять не может, и скобки подзапроса не закрыты.
Исправить ссылки на несуществующие объекты.
CTE prm_dt закомментирован, но используется в course и в расчётах (prm_dt.REPORTING_DATE). Замените на prm_dt_range.DATE_END.
В course нужно FROM prm_dt_range, DWKR_02.COURSE_NBRB_MV cr WHERE cr.COURSE_DATE < prm_dt_range.DATE_END.
Переменной in_DATE в процедуре нет. Везде в MONTHS_BETWEEN подставьте prm_dt_range.DATE_END.
В kd_begin_crncy везде стоит kd_end. Должно быть FROM prm_dt_range, kd_begin INNER JOIN ..., иначе валюты на начало периода считаются по договорам конца периода. Ошибки компиляции не будет, но результат окажется неверным.
Несовпадение колонок в INSERT.
В списке 16 колонок (RISK_GROUP_..., MAIN_DEBT_BYN_RISK_GROUP_1..6_END и т.д.), а SELECT возвращает 18 значений, причём это сроки (KD_TERM_...). Будет ORA-00913, когда дойдёте до этого места.
Скорее всего, таблица REPORT_FS10_RESULT и функция GET_FS10_RESULT рассчитаны на группы риска, а запрос написан под сроки. Нужно привести к одному виду: либо переделать таблицу, тип REPORT_FS10_RESULT_TBL_TP и курсор, либо изменить список колонок вставки.
Порядок в CASE KD_TERM_MONTHS_GROUP. Проверка END_DATE_OSN IS NULL стоит после сравнений с MONTHS_BETWEEN, поэтому при NULL ветка 1000 фактически сработает не там, где задумано. Перенесите её первой.
Фильтры не применяются. CTE prm_bank и prm_borr объявлены, но нигде не используются. Значит, in_BANK_ID, группы источников и тип заёмщика на результат не влияют. Проверьте, так ли задумано.
Мелочь: в одном из логов указано REPORT_FS6.PROC_FS10 вместо REPORT_FS10.