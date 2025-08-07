import requests
import pandas as pd

def get_data(url, max_retries=10):
  data_list = []
  page = 33
  retries = 0
  
  while True:
    try:
      response = requests.get(url + f"&page={page}&per_page=50")
      if response.status_code == 200:
        print(response)
        data = response.json()
        if  not data['results']:
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
  programs = []
  for data in data_list:
    programs = data['latest.programs.cip_4_digit'] if "latest.programs.cip_4_digit" in data else None
    for program in programs:
      try:
        mapped_data.append({
          'unitid': data['id'],
          'opeid6': program['ope6_id'],
          'control_l': program['school']['type'],
          'main': program['school']['main_campus'],
          'cipcode': program['code'],
          'cipdesc': program['title'],
          'credlev': program['credential']['level'],
          'creddesc': program['credential']['title'],
          'ipedscount2': program['counts']['ipeds_awards2'],
          'earn_count_nwne_hi_1yr': program['earnings']['highest']['1_yr']['not_working_not_enrolled']['overall_count'],
          'earn_count_wne_hi_1yr': program['earnings']['highest']['1_yr']['working_not_enrolled']['overall_count'],
          'earn_count_male_wne_1yr': program['earnings']['1_yr']['working_not_enrolled']['male_count'],
          'earn_male_wne_mdn_1yr': program['earnings']['1_yr']['male_median_earnings'],
          'earn_count_nomale_wne_1yr': program['earnings']['1_yr']['working_not_enrolled']['nonmale_count'],
          'earn_nomale_wne_mdn_1yr': program['earnings']['1_yr']['nonmale_median_earnings'],
          'earn_mdn_1yr': program['earnings']['1_yr']['overall_median_earnings'],
          'earn_count_nwne_1yr': program['earnings']['1_yr']['not_working_not_enrolled']['overall_count'],
          'earn_count_wne_1yr': program['earnings']['1_yr']['working_not_enrolled']['overall_count'],
          'earn_count_nwne_4yr': program['earnings']['4_yr']['not_working_not_enrolled']['overall_count'],
          'earn_count_wne_4yr': program['earnings']['4_yr']['working_not_enrolled']['overall_count'],
          'earn_mdn_4yr': program['earnings']['4_yr']['overall_median_earnings'],
          'earn_count_male_wne_4yr': program['earnings']['4_yr']['working_not_enrolled']['male_count'],
          'earn_male_wne_mdn_4yr': program['earnings']['4_yr']['male_median_earnings'],
          'earn_count_nomale_wne_4yr': program['earnings']['4_yr']['working_not_enrolled']['nonmale_count'],
          'earn_nomale_wne_mdn_4yr': program['earnings']['4_yr']['nonmale_median_earnings'],
          'earn_count_high_cred_4yr': program['earnings']['4_yr']['overall_count_awarded_higher_credential'],
          'earn_gt_threshold_1yr': program['earnings']['1_yr']['overall_count_more_than_HS_Grad'],
          'earn_gt_threshold_4yr': program['earnings']['4_yr']['overall_count_more_than_HS_Grad'],
          'earn_in_state_1yr': program['earnings']['1_yr']['overall_count_working_in_institution_state'],
          'earn_in_state_4yr': program['earnings']['4_yr']['overall_count_working_in_institution_state'],
          'debt_all_stgp_eval_mdn': program['debt']['staff_grad_plus']['all']['eval_inst']['median_payment'],
          'debt_all_stgp_eval_mdn10yrpay': program['debt']['staff_grad_plus']['all']['eval_inst']['median_payment']
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
  url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?fields=id,school.name,latest.programs.cip_4_digit&api_key=RpnYmcl8jZgEaf18fb5wjRGtaIdoaxfpdgdsmKx9"
  data_list = get_data(url)
  mapped_data_list = map_nested_data(data_list)
  save_to_xlsx(mapped_data_list, "cs_field_study_govs_33.xlsx")