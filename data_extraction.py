from bs4 import BeautifulSoup
from urllib import request
from urllib import error
from selenium import webdriver
import os
import csv

def get_the_info(url):
    global log_file
    try:
        response = request.urlopen(url)
    except error.URLError as e:
        if hasattr(e,'reson'):
            print("Failed to reach server",file=log_file)
            print("Reason:", e.reason,file=log_file)
            print("URL:",url,file=log_file)
        elif hasattr(e,'code'):
            print("The server couldn\'t fulfill the request",file=log_file)
            print("Error code:", e.code,file=log_file)
            print("URL:",url,file=log_file)            
        return None

    # Create soup
    soup = BeautifulSoup(response, 'html.parser')
    
    # Getting year from the url
    YEAR = url.split("/")[4][:4]
    # Getting name from the page
    NAME = soup.h1.text.strip()
    # Getting the overview text
    BACH_OVERVIEW = soup.find_all("div",class_="aside-quick-stats")[0].p.text
    if BACH_OVERVIEW is None:
        BACH_OVERVIEW = "--None--"

    # Testing for instituition type by word possession
    if not BACH_OVERVIEW:
        INSTITUTION_TYPE="INSTITUTION_TYPE"
    elif "private" in BACH_OVERVIEW:
        INSTITUTION_TYPE="private"
    elif "public" in BACH_OVERVIEW:
        INSTITUTION_TYPE="public"
    elif "proprietary" in BACH_OVERVIEW:
        INSTITUTION_TYPE="proprietary"
    else:
        INSTITUTION_TYPE="---None---"

    # Setting a location info1 to be searched for key word 
    info1 = soup.find_all("div",class_="aside-quick-stats")[0]

    # Searching for a foundation year
    for i in range(len(info1.find_all("td"))):
        if "ear found" in info1.find_all("td")[i].text:
            YEAR_FOUNDED = info1.find_all("td")[i+1].text

    # Finding total enrollment value
    TOTAL_ENROLLMENT = soup.find_all("tr",class_="total_enr_all_cy")[0].span.text.strip()

    # Three try/except clauses testing for various rankings and scores
    try:
        FAC_CRED_RANK = soup.find_all("tr",class_="v_faculty_and_credentials_rank")[0].span.text.strip()
        FAC_CRED_SCORE = soup.find_all("tr",class_="v_faculty_and_credentials_score")[0].span.text.strip()
    except:
        FAC_CRED_RANK = "--None--"
        FAC_CRED_SCORE = "--None--"
    try:
        STUD_SERV_TECH_RANK = soup.find_all("tr",class_="v_student_services_and_technology_rank")[0].span.text.strip()
        STUD_SERV_TECH_SCORE = soup.find_all("tr",class_="v_student_services_and_technology_score")[0].span.text.strip()
    except:
        STUD_SERV_TECH_RANK = "--None--"
        STUD_SERV_TECH_SCORE = "--None--"
    try:
        STUD_ENGAGEMENT_RANK = soup.find_all("tr",class_="v_engagement_and_accreditation_rank")[0].span.text.strip()
        STUD_ENGAGEMENT_SCORE =soup.find_all("tr",class_="v_engagement_and_accreditation_score")[0].span.text.strip()
    except:
        STUD_ENGAGEMENT_RANK = "--None--"
        STUD_ENGAGEMENT_SCORE = "--None--"

    # Full/parttime instrutional faculty values are found
    FULL_TIME_INSTRUCTIONAL = soup.find_all("tr",class_="ft_faculty_count")[0].span.text.strip()
    PART_TIME_INSTRUCTIONAL = soup.find_all("tr",class_="pt_faculty_count")[0].span.text.strip()

    # Finding enrollnment numbers for average age of the students
    AVG_STUD_AGE = soup.find_all("tr",class_="average_enrollment_age")[0].span.text.strip()

    # Setting base location for tuition information
    tuition = soup.find(class_="fields free_paying")
    # creating an list of the coloumn contents
    sf = tuition.find_all("td")
    # PreSetting values incase they are not included in coloumn
    INSTATE_TUITION_PER_CREDIT = "---None---"
    OUTSTATE_TUITION_PER_CREDIT = "---None---"
    INTERNATIOONAL_TUITUION_PER_CREDIT = "---None---"
   
    # Search each column for different tuition types
    for i in range(len(sf)):
        if "In-state, out-of-district tuition for U.S. students (per credit)" in sf[i].contents[0]:
            INSTATE_TUITION_PER_CREDIT = sf[i+1].span.string.strip()
        elif "Tuition for U.S. students (per credit)" in sf[i].contents[0]:
            INSTATE_TUITION_PER_CREDIT = sf[i+1].span.string.strip()
            OUTSTATE_TUITION_PER_CREDIT = INSTATE_TUITION_PER_CREDIT              
        elif "Out-of-state tuition for U.S. students (per credit)" in sf[i].contents[0]:
            OUTSTATE_TUITION_PER_CREDIT = sf[i+1].span.string.strip()
        elif "Tuition for international students (per credit)" in sf[i].contents[0]:
            INTERNATIOONAL_TUITUION_PER_CREDIT = sf[i+1].span.string.strip()

    # the url used to find the site
    ARCHIVE_LINK = url
        
    return (YEAR,
            NAME,
            BACH_OVERVIEW,
            INSTITUTION_TYPE,
            YEAR_FOUNDED,
            TOTAL_ENROLLMENT,
            FAC_CRED_RANK,
            FAC_CRED_SCORE,
            STUD_SERV_TECH_RANK,
            STUD_SERV_TECH_SCORE,
            STUD_ENGAGEMENT_RANK,
            STUD_ENGAGEMENT_SCORE,
            FULL_TIME_INSTRUCTIONAL,
            PART_TIME_INSTRUCTIONAL,
            AVG_STUD_AGE,
            INSTATE_TUITION_PER_CREDIT,
            OUTSTATE_TUITION_PER_CREDIT,
            INTERNATIOONAL_TUITUION_PER_CREDIT,
            ARCHIVE_LINK)


if __name__ == "__main__":

    # Opening a file containing a listing of college urls
    # BACH i.e. bachelors
    school_sites = open('BACH.txt','r')
    SCHOOL_SITES = []
    # Create a list of the urls
    for site in school_sites:
        SCHOOL_SITES.append(site[:-1])

    # Open a log and output file
    log_file = open('the_log2.txt','a')
    school_info = open('the_college_data2.csv','a')
    # Create output writer
    csvwriter = csv.writer(school_info,dialect='unix')
    # create a PhantomJS webdriver instance
    driver = webdriver.PhantomJS()
    # Make a dirctory for screenshots
    os.mkdir("the_ScreenShots")

    # for each url grab the school informaiton and take a screenshot
    # save the screenshot in the created directory
    for url in SCHOOL_SITES:
        print(url)
        # Clearing variable information for each attepmted url
        the_school_info = []
        try:
            driver.get(url)
            # parsing  the url for use in nameing format
            url_Split = url.split("/")
            # save screenshot containing "date-university_name"
            driver.save_screenshot("the_ScreenShots/"+url_Split[4]+"-"+url_Split[-2]+".png")
            # use the above function to get the needed values returned as a tuple
            the_school_info = get_the_info(url)
        except:
            print("Not complete:",url,file=log_file)
            continue
        
        # as long as there is a info write to file the contents
        if the_school_info:
            csvwriter.writerow(the_school_info)
    
    school_info.close()
    log_file.close()
    school_sites.close()
