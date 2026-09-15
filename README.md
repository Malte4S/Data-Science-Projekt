# Data-Science-Projekt
A Data Science Project done as part of the Data Science Project course. This project is investigating 6 research questions around energy and weather using public APIs. The results are presented in an interactive Streamlit web app. \
The world we live in is increasingly shifting towards weather-dependent, renewable sources of energy such as solar, wind, and hydro power. As this trend continues, changing weather patterns play a growing role in shaping a country's national energy production. In this project, we examine how renewable energy generation correlates with these conditions, and how volatile and vulnerable a country's energy supply becomes as a result. 


# Research Questions
We explore this across six research questions, covering drought and hydropower, wind performance, and the volatility of power generation, trade, and prices across different European bidding zones: 


**RQ1:** How does a Heatwave affect Solar and Hydro Generation in Spain between 2015 and 2024? \
**RQ2:** In drought years, do countries with high hydro dependency show an increase in fossil fuel backup generation compared to countries with a diversified energy mix? \
**RQ3:** Do countries with higher average wind speeds generate proportionally more electricity per installed wind turbine capacity than countries with lower wind speeds, and which countries over or underperform relative to their wind potential? \
**RQ4:** Has the growing share of weather-dependent renewable energy increased the volatility of national electricity generation during extreme weather events, and to what extent are cross-border trades effected? \
**RQ5:** To what extent do countries with a higher share of renewables in their energy mix show greater electricity price volatility during extreme weather events compared to countries with a fossil-fuel-dominated mix? \
**RQ6:** How is renewable electricity generation associated with regional meteorological conditions between northern and southern European countries?​ \


# Datasources
The Raw Data was gathered from multiple sources. The main once are:
- Energy-Charts Api
- Open-Meto Api

Energy-Charts was selected because it provides detailed and comparable energy data for multiple European countries, while Open-Meteo provides historical weather data for the locations and timeframes required for our analyses.

A challenging part of the data acquisition was the rate limit, mainly from the Open-Meteo API. The API allows for 10,000 daily API calls. Since we were interested in multiple features across many data points, this limit was reached several times. Thus, the data acquisition had to take place over multiple days. Example calls for these API's can be found in the “API-Test” Notebook in the “raw_data” folder.

In addition, multiple smaller sources were used to gather more specific information for some research questions: 
- Global Wind Atlas
- Our World in Data
- World Bank Open Data
- Global Energy Monitor


# Raw Data
**Energy-Charts Api:** 

The Energy-Chars Api provides multiple Endpoints for different datasets. The relevant once for this Project where the following once:
- installed_power: Contains statistics on installed power capacity for European countries. It records the installed capacity in GW per production type. While this does not show how much electricity is actually generated, it indicates the maximum installed capacity of a country and the technologies it relies on. The data is available by year and goes back to at least 2014, and sometimes further depending on the country. An example can be found in  “raw_data\InstalledPowerByCountry”.
- public_power: Contains data on actual electricity generation by production type. In addition, it contains information on electricity traded within the given timeframe. The data is available for European countries in intervals of up to 15 minutes and goes back to at least 2017. An example can be found in “raw_data\Generationdata”.
- price: Contains the day-ahead electricity price for each European bidding zone in EUR/MWh. The data has an hourly resolution and goes back to at least 2015. An example can be found in “raw_data\BiddingZones”.

**Open-Meteo Api:**

The Open-Meteo API provides different services for recent and historical weather data. For our research, we relied on the historical weather API, which provides data going back to 1940. Weather variables such as temperature and relative humidity can be accessed for a defined latitude and longitude over a given timeframe, including data at a daily resolution .
An example can be found in “raw_data\Weatherdata”.

**Smaller Sources:**

**Global Wind Atlas:**
GWA provides all the data around wind for RQ3. Data was only collected from the year 2025.

**Our World in Data:**
Used for worldwide energy data in the timeframe 2005-2023 for RQ2. 

**World Bank Open Data:**
Provides RQ2 with a crucial parameter: spei_12, is an indicator for drought.  

**Global Energy Monitor:**
Used for worldwide energy data


# Datarefinment
**RQ1:**

**RQ2 and RQ3:** The folders 'Drought - Pipeline' and 'Wind-Pipeline' each contain a notebook and the resulting CSV files from it.

**RQ4 and RQ5**: The Transformation Notebooks for these questions can be found in the folders “Transformation - Generation Volatility” and “Transformation - Price Volatility”. In these notebooks, the raw data was filtered to the required timeframes and enriched by calculating additional variables necessary for the analyses. This includes identifying extreme weather event days and calculating relevant values for electricity generation, cross-border trade, and prices. During the transformation process, normalized values were used to make comparability between countries easier. The resulting datasets were then exported and used as the final data sources for the website.

**RQ6:**


# Website
The website was built and deployed with Python and Streamlit. \
A separate page was created for each research question, with each group member being responsible for up to two questions. Since every research question has its own page, development could largely take place independently without major conflicts between group members.  \
For our visualizations, we mainly used Matplotlib. One of the main reasons for this choice was our previous experience with the library from earlier courses. It also allowed us to use the same visualization approaches during local testing in notebooks and later within the Streamlit application. In some cases, visualizations were created directly using Streamlit's built-in functionality. \
The website uses the refined datasets that were prepared and tested beforehand. This ensures that the visualizations work with already processed data and reduces the amount of data transformation that needs to be performed by the website itself.


# Websitenavigation
To navigate the website, use the navigation menu on the left. Each research question has its own dedicated page. On each page, you will find explanations, results, and at least three visualizations. These visualizations can be altered using the provided selectors and sliders. Common filters include year, weather event type, country, or generation type, depending on the respective research question.


# Use of LLM's
LLM’s were used for multiple purposes in this project:
- Refinement of Research Questions: During the initial phase of the project, LLM’s were used as a source of inspiration and to refine our research questions to meet the required level of complexity for the course. 
- Explanations and Understanding: During the data refinement and website development processes, we occasionally encountered functions or concepts that we were unfamiliar with, such as specific Streamlit functionalities. LLM’s were used to gain a better understanding of these functions and concepts before using them in the project. 
- Code Generation: LLM’s were used to support code generation in cases where the best solution to a problem was not immediately obvious. For example, they were used when exploring approaches for defining extreme weather events and implementing their identification for RQ4 and RQ5. The generated suggestions were evaluated, adapted, and integrated according to the specific requirements of our analyses.


# Link to website
https://data-science-projektgit-zvrcrkkii5ahrl2diyoxpi.streamlit.app/

