# Data-Science-Projekt
A Data Science Project done as part of the Data Science Project course. This project is investigating 6 research questions around energy and weather using public APIs. The results are presented in an interactive Streamlit web app. \
The world we live in is increasingly shifting towards weather-dependent, renewable sources of energy such as solar, wind, and hydro power. As this trend continues, changing weather patterns play a growing role in shaping a country's national energy production. In this project, we examine how renewable energy generation correlates with these conditions, and how volatile and vulnerable a country's energy supply becomes as a result. 


# Research Questions
We explore this across six research questions, covering drought and hydropower, wind performance, and the volatility of power generation, trade, and prices across different European bidding zones: 


RQ1: How does a Heatwave affect Solar and Hydro Generation in Spain between 2015 and 2024? \
RQ2: In drought years, do countries with high hydro dependency show an increase in fossil fuel backup generation compared to countries with a diversified energy mix? \
RQ3: Do countries with higher average wind speeds generate proportionally more electricity per installed wind turbine capacity than countries with lower wind speeds, and which countries over or underperform relative to their wind potential? \
RQ4: Has the growing share of weather-dependent renewable energy increased the volatility of national electricity generation during extreme weather events, and to what extent are cross-border trades effected? \
RQ5: To what extent do countries with a higher share of renewables in their energy mix show greater electricity price volatility during extreme weather events compared to countries with a fossil-fuel-dominated mix? \
RQ6: How is renewable electricity generation associated with regional meteorological conditions between northern and southern European countries?​ \


# Datasources
The Raw Data was gathered from multiple sources. The main once are:
- Energy-Charts Api
- Open-Meto Api  \
A challenging part in the data acquisition here was the rate limit, mainly from Open-Meteo Api. The Api allows for 10.000 daily Api calls. But since we were interested in multiple features over many data points, this limit was hit many times. Thus the data acquisition had to take place over multiple days. Example calls can be found in the API-Test Notebook in the “raw_data” folder. \
In addition to that, multiple smaller sources were used for gathering some more specific information for some research quests. THe are the following:
- Global Wind Atlas
- Our World in Data
- World Bank Open Data
- Global Energy Monitor


# Raw Data
Energy-Charts Api: \
The Energy-Chars Api provides multiple Endpoints for different datasets. The relevant once for this Project where the following once:
- installed_power: Contains Information installed power statistics for European countries. That means that it records what the country actually has installed in GW per Productiontype. While this doesn't show how much is actually produced it shows the maximum potential of a country and what each country prioritizes. The data is accessible per year and goes back to at least 2014, sometimes further depending on the country. (An example can be found in the folder “raw_data\InstalledPowerByCountry”)
- public_power: This endpoint contains data about the actual power production per Productiontype. On top of that it also contains the amount of power traded in the given timeframe. It is available for every European country in up to 15 minute intervals and goes back to at least 2017. (An example can be found in the folder “raw_data\Generationdata”)
- price: This dataset contains the day-ahead price for each European Bidding Zone in Euro/MWh. The Data has an hourly interval that goes back to at least 2015. (An example can be found in the folder “raw_data\BiddingZones”) \
Open-Meteo Api:
The Open-Meteo Api has two versions. One provides recent data going back to the last 3 months. The other is historical and can provide data going back to 1940. For our research we relied on the historical version. From here data about all kinds of weather conditions like Temperature, relative humidity, etc can be accessed for a defined Latitude and Longitude for a given timeframe on a daily basis.
(An example can be found in the folder “raw_data\Weatherdata”)


Global Wind Atlas: \
GWA provides all the data around wind for RQ3. Data was only collected from the year 2025. \
Our World in Data: \
Used for worldwide energy data in the timeframe 2005-2023 for RQ2. \
World Bank Open Data: \
Provides RQ2 with a crucial parameter: spei_12, is an indicator for drought. \
Global Energy Monitor: \
Used for worldwide energy data \


# Datarefinment
RQ1: \
RQ2 and RQ3: The folders 'Drought - Pipeline' and 'Wind-Pipeline' each contain a notebook and the resulting CSV files from it. \
RQ4 and RQ5: The Transformation Notebooks for these questions can be found in the folders “Transformation - Generation Volatility” and “Transformation - Price Volatility”. In these Notebooks the raw data was filtered to the proper timeframes, enriched by calculating columns necessary for our project (this includes figuring out the weather event days, calculating values for production, trades and prices amongst others) and exported as the final data used for the website. During the transformation it was ensured that the data of different countries is comparable though percentages as well as making sure that no issues of missing values arise. \
RQ6: \


# Website
The website was built and deployed with Python and Streamlit. \
For each Research question we set up a separate page, and each Group Member got a set of up to 2 questions to work on. Since every Question has its own page, we never ran into problems of our work conflicting with one anothers, meaning the building itself went smoothly. \
For our Visuals we mainly used the Matplotlib library already integrated in python. THe main reason here was that it has come up in previous courses of our studies and it was easy to use in both our testing phases in our local notebooks as well as on the website. On a few occasions the visualizations were also built using the streamlit tools. \
The data for the Website was the already refined version we prepared and tested beforehand, to ensure that the Visuals would work as intended and the website had to bear less load for transformations.


# Websitenavigation
To find your way around the website use the navigation menu on the left. Each Research question has its own page. On said page you will find explainitions, results and atleast 3 visuals. These visuals can be filtered by using the Selectors and slider provided. Usual Filters include Year, Weather Event type or generation type.


# Regarding LLM's
LLM’s were used for multiple purposes in this project:
- Refinement of Research Questions: During the starting phase of the Project LLM’s were used to get inspiration and to get our developed Research Questions to the required complexity levels of the course.
- Basic explanations: During our data refinement and website building processes it often came to situations where it wasn't clear how a certain function (for example sliders in Streamlit) work. Thus LLM’s were used to gain further understanding of these functions so they can be used for our purposes.
- Code Generation: LLM’s were used for code generation in cases where the solution to a problem wasn’t immediately obvious (for example defining what counts as an extreme weather event and how to implement the code to figure it out for RQ4 and RQ5). The returned suggestions were then transferred and adapted to fit our purposes.


# Link to website
https://data-science-projektgit-zvrcrkkii5ahrl2diyoxpi.streamlit.app/

