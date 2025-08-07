import requests
import pandas as pd

def get_data(url, max_retries=10):
  data_list = []
  page = 0
  retries = 0
  
  while True:
    try:
      response = requests.get(url + f"&page={page}&per_page=50")
      if response.status_code == 200:
        print(response)
        data = response.json()
        if not data['results']:
          break
        data_list.extend(data['results'])
        page += 1
        retries = 0
      else:
        if retries < max_retries:
          retries += 1
          print(f"Error: Unable to fetch data for page {page}. Retrying ({retries}/{max_retries})...")
        else:
          print(f"Error: Unable to fetch data for page {page} after {max_retries} retries. Aborting.")
          retries = 0
          page += 1
    except (requests.HTTPError) as e:
      if retries < max_retries:
        retries += 1
        print(f"Error: {e}. Retrying ({retries}/{max_retries})...")
      else:
        print(f"Error: {e} after {max_retries} retries. Aborting.")
        page += 1
        retries = 0

  return data_list

def map_nested_data(data_list):
  mapped_data = []
  for data in data_list:
    try:
      mapped_data.append({
        'unitid': data['id'],
        'instnm': data['school.name'],
        'c150_4': data['latest.completion.completion_rate_4yr_150nt'],
        'c150_l4': data['latest.completion.completion_rate_less_than_4yr_150nt'],
        'cntover150_1yr': data['latest.earnings.1_yr_after_completion.overall_count_over_poverty_line'],
        'count_wne_1yr': data['latest.earnings.1_yr_after_completion.working_not_enrolled.overall_count'],
        'unemp_rate': data['latest.student.demographics.unemployment'],
        'gt_threshold_1yr': data['latest.earnings.1_yr_after_completion.overall_count_over_poverty_line'],
        'opeflag': data['school.title_iv.eligibility_type'],
        'actcm25': data['latest.admissions.act_scores.25th_percentile.cumulative'],
        'actcm75': data['latest.admissions.act_scores.75th_percentile.cumulative'],
        'actcmmid': data['latest.admissions.act_scores.midpoint.cumulative'],
        'acten25': data['latest.admissions.act_scores.25th_percentile.english'],
        'acten75': data['latest.admissions.act_scores.75th_percentile.english'],
        'actenmid': data['latest.admissions.act_scores.midpoint.english'],
        'actmt25': data['latest.admissions.act_scores.25th_percentile.math'],
        'actmt75': data['latest.admissions.act_scores.75th_percentile.math'],
        'actmtmid': data['latest.admissions.act_scores.midpoint.math'],
        'adm_rate': data['latest.admissions.admission_rate.overall'],
        'admcon7': data['latest.admissions.test_requirements'],
        'alias': data['school.alias'],
        'c100_4': data['latest.completion.completion_rate_4yr_100nt'],
        'c100_4_pooled': data['latest.completion.completion_rate_four_year_100_pooled'],
        'c100_l4': data['latest.completion.completion_rate_less_than_4yr_100nt'],
        'c100_l4_pooled': data['latest.completion.completion_rate_lt_four_year_100_pooled'],
        'c150_4': data['latest.completion.completion_rate_4yr_150nt'],
        'c150_l4': data['latest.completion.completion_rate_less_than_4yr_150nt'],
        'ccbasic':  data['school.carnegie_basic'],
        'ccsizset': data['school.carnegie_size_setting'],
        'ccugprof': data['school.carnegie_undergrad'],
        'ciptitle1': data['latest.academics.program_reporter.program_1.cip_6_digit.title'],
        'ciptitle2': data['latest.academics.program_reporter.program_2.cip_6_digit.title'],
        'ciptitle3': data['latest.academics.program_reporter.program_3.cip_6_digit.title'],
        'ciptitle4': data['latest.academics.program_reporter.program_4.cip_6_digit.title'],
        'ciptitle5': data['latest.academics.program_reporter.program_5.cip_6_digit.title'],
        'ciptfbsannual1': data['latest.cost.program_reporter.program_1.cip_6_digit.annualized'],
        'ciptfbsannual2': data['latest.cost.program_reporter.program_2.cip_6_digit.annualized'],
        'ciptfbsannual3': data['latest.cost.program_reporter.program_3.cip_6_digit.annualized'],
        'ciptfbsannual4': data['latest.cost.program_reporter.program_4.cip_6_digit.annualized'],
        'ciptfbsannual5': data['latest.cost.program_reporter.program_5.cip_6_digit.annualized'],
        'city': data['school.city'],
        'comp_orig_yr4_rt': data['latest.completion.title_iv.completed_by.4yrs'],
        'control': data['school.ownership'],
        'death_yr2_rt': data['latest.completion.title_iv.died_by.2yrs'],
        'debt_mdn': data['latest.aid.loan_principal'],
        'distanceonly': data['school.online_only'],
        'hi_inc_debt_mdn': data['latest.aid.median_debt.income.greater_than_75000'],
        'highdeg': data['school.degrees_awarded.highest'],
        'iclevel': data['school.institutional_characteristics.level'],
        'insturl': data['school.school_url'],
        'latitude': data['location.lat'],
        'lo_inc_debt_mdn': data['latest.aid.median_debt.income.0_30000'],
        'locale': data['school.locale'],
        'longitude': data['location.lon'],
        'main': data['school.main_campus'],
        'md_earn_wne_1yr': data['latest.earnings.1_yr_after_completion.median'],
        'md_earn_wne_4yr': data['latest.earnings.4_yrs_after_completion.median'],
        'md_inc_debt_mdn': data['latest.aid.median_debt.income.30001_75000'],
        'mdcost_pd': data['latest.cost.avg_net_price.consumer.median_by_pred_degree'],
        'npcurl': data['school.price_calculator_url'],
        'numbranch': data['school.branches'],
        'opeid': data['ope8_id'],
        'opeid6': data['ope6_id'],
        'pctfloan': data['latest.aid.federal_loan_rate'],
        'pctpell': data['latest.aid.pell_grant_rate'],
        'pftftug1_ef': data['latest.student.share_first.time_full.time'],
        'preddeg': data['school.degrees_awarded.predominant'],
        'region': data['school.region_id'],
        'relaffil': data['school.religious_affiliation'],
        'ret_ft4': data['latest.student.retention_rate.four_year.full_time'],
        'ret_ft4_pooled_supp': data['latest.student.retention_rate_suppressed.four_year.full_time_pooled'],
        'ret_ftl4': data['latest.student.retention_rate.lt_four_year.full_time'],
        'ret_ftl4_pooled_supp': data['latest.student.retention_rate_suppressed.lt_four_year.full_time_pooled'],
        'sat_avg': data['latest.admissions.sat_scores.average.overall'],
        'satmt25': data['latest.admissions.sat_scores.25th_percentile.math'],
        'satmt75': data['latest.admissions.sat_scores.75th_percentile.math'],
        'satmtmid': data['latest.admissions.sat_scores.midpoint.math'],
        'satvr25': data['latest.admissions.sat_scores.25th_percentile.critical_reading'],
        'satvr75': data['latest.admissions.sat_scores.75th_percentile.critical_reading'],
        'satvrmid': data['latest.admissions.sat_scores.midpoint.critical_reading'],
        'stabbr': data['school.state'],
        'stufacr': data['latest.student.demographics.student_faculty_ratio'],
        'trans_4_pooled': data['latest.completion.transfer_rate.4yr.full_time_pooled'],
        'trans_l4_pooled': data['latest.completion.transfer_rate.less_than_4yr.full_time_pooled'],
        'tuitionfee_in': data['latest.cost.tuition.in_state'],
        'tuitionfee_out': data['latest.cost.tuition.out_of_state'],
        'ug': data['latest.student.enrollment.all'],
        'ugds': data['latest.student.size'],
        'zip': data['school.zip']
      })
    except KeyError as e:
      print(f"Error: Unable to map data for UNITID {data['id']}.")
      print(f"Missing key: {e}")
      continue
  return mapped_data

def save_to_xlsx(mapped_data_list, file_name):
  df = pd.DataFrame(mapped_data_list)
  df.to_excel(file_name, index=False, engine="openpyxl")

if __name__ == "__main__":
  url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?fields=id,school.name,latest.admissions.act_scores.25th_percentile.cumulative,latest.admissions.act_scores.75th_percentile.cumulative,latest.admissions.act_scores.midpoint.cumulative,latest.admissions.act_scores.25th_percentile.english,latest.admissions.act_scores.75th_percentile.english,latest.admissions.act_scores.midpoint.english,latest.admissions.act_scores.25th_percentile.math,latest.admissions.act_scores.75th_percentile.math,latest.admissions.act_scores.midpoint.math,latest.admissions.admission_rate.overall,latest.admissions.test_requirements,school.alias,latest.completion.completion_rate_4yr_100nt,latest.completion.completion_rate_four_year_100_pooled,latest.completion.completion_rate_less_than_4yr_100nt,latest.completion.completion_rate_lt_four_year_100_pooled,latest.completion.completion_rate_4yr_150nt,latest.completion.completion_rate_less_than_4yr_150nt,school.carnegie_basic,school.carnegie_size_setting,school.carnegie_undergrad,latest.academics.program_reporter.program_1.cip_6_digit.title,latest.academics.program_reporter.program_2.cip_6_digit.title,latest.academics.program_reporter.program_3.cip_6_digit.title,latest.academics.program_reporter.program_4.cip_6_digit.title,latest.academics.program_reporter.program_5.cip_6_digit.title,latest.cost.program_reporter.program_1.cip_6_digit.annualized,latest.cost.program_reporter.program_2.cip_6_digit.annualized,latest.cost.program_reporter.program_3.cip_6_digit.annualized,latest.cost.program_reporter.program_4.cip_6_digit.annualized,latest.cost.program_reporter.program_5.cip_6_digit.annualized,school.city,latest.completion.title_iv.completed_by.4yrs,school.ownership,latest.completion.title_iv.died_by.2yrs,latest.aid.loan_principal,school.online_only,latest.aid.median_debt.income.greater_than_75000,school.degrees_awarded.highest,school.institutional_characteristics.level,school.school_url,location.lat,latest.aid.median_debt.income.0_30000,school.locale,location.lon,school.main_campus,latest.earnings.1_yr_after_completion.median,latest.earnings.4_yrs_after_completion.median,latest.aid.median_debt.income.30001_75000,latest.cost.avg_net_price.consumer.median_by_pred_degree,school.price_calculator_url,school.branches,ope8_id,ope6_id,latest.aid.federal_loan_rate,latest.aid.pell_grant_rate,latest.student.share_first.time_full.time,school.degrees_awarded.predominant,school.region_id,school.religious_affiliation,latest.student.retention_rate.four_year.full_time,latest.student.retention_rate_suppressed.four_year.full_time_pooled,latest.student.retention_rate.lt_four_year.full_time,latest.student.retention_rate_suppressed.lt_four_year.full_time_pooled,latest.admissions.sat_scores.average.overall,latest.admissions.sat_scores.25th_percentile.math,latest.admissions.sat_scores.75th_percentile.math,latest.admissions.sat_scores.midpoint.math,latest.admissions.sat_scores.25th_percentile.critical_reading,latest.admissions.sat_scores.75th_percentile.critical_reading,latest.admissions.sat_scores.midpoint.critical_reading,school.state,latest.student.demographics.student_faculty_ratio,latest.completion.transfer_rate.4yr.full_time_pooled,latest.completion.transfer_rate.less_than_4yr.full_time_pooled,latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,latest.student.enrollment.all,latest.student.size,school.zip,latest.completion.completion_rate_4yr_150nt,latest.completion.completion_rate_less_than_4yr_150nt,latest.earnings.1_yr_after_completion.overall_count_over_poverty_line,latest.earnings.1_yr_after_completion.working_not_enrolled.overall_count,latest.student.demographics.unemployment,school.title_iv.eligibility_type&api_key=RpnYmcl8jZgEaf18fb5wjRGtaIdoaxfpdgdsmKx9"
  data_list = get_data(url)
  mapped_data_list = map_nested_data(data_list)
  save_to_xlsx(mapped_data_list, "cs_institut_govs.xlsx")