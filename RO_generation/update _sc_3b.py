import os
from rohub import rohub, settings
import pandas as pd
import csv
import urllib.request
import json
import plotly.express as px
import kaleido

rohub.login(username="rpalma", password="gato_domestico")

os.mkdir("/Users/sam/Downloads/scenario3B")

#to download the text from url
url_of_content="http://webservices.ingv.it/fdsnws/event/1/query?starttime=1985-01-01T00%3A00%3A00&endtime=2021-06-30T23%3A59%3A59&minmag=7&maxmag=10&mindepth=-10&maxdepth=1000&minlat=-90&maxlat=90&minlon=-180&maxlon=180&minversion=100&orderby=time-asc&format=text&limit=10000"
urllib.request.urlretrieve(url_of_content,"/Users/sam/Downloads/scenario3B/test.txt")

#to write as csv
df = pd.read_fwf("/Users/sam/Downloads/scenario3B/test.txt")
df.to_csv("/Users/sam/Downloads/scenario3B/test.csv", index=False)
#to cleann the downloaed file
with open ("/Users/sam/Downloads/scenario3B/test.csv","r") as file1, open ("/Users/sam/Downloads/scenario3B/test_1.csv","w") as file2:
    content1 = file1.read()
    content2 = content1.replace("#", "")
    content3=content2.replace("|", ";")
    content4=content3.replace(",", "")
    content5=content4.replace(";", ",")
    content6 = content5.replace('"', '')
    content7=content6.replace('--', '')
    file2.write(content7)

#to make the temlate csv file
df = pd.read_csv("/Users/sam/Downloads/scenario3B/test_1.csv")
df["title"] = "Earthquake with magnitude of" +" "+ df["MagType"]+' '+ df["Magnitude"].astype(str)+" "+"on date and time"+' '+ df["Time"].astype('datetime64[ns]').astype(str)+' '+"(UTC)"+" "+"in region"+" "+df["EventLocationName"]
df["description"]  = df["title"]+ " "+"and geographic coordinates (lat, lon)"+" "+df["Latitude"].astype(str)+", "+df["Longitude"].astype(str)+" at depth"+" "+df["Depth/Km"].astype(str)+" km. "+"The earthquake was located by: Sala Sismica INGV-Roma. Data and results are taken from the website managed by Istituto Nazionale di Geofisica e Vulcanologia and they are licensed under a Creative Commons Attribution 4.0 International License. ISIDe Working Group at National Earthquake Observatory benefited from funding provided by the Italian Presidenza del Consiglio dei Ministri, Dipartimento della Protezione Civile."
df["Event_url"] ="http://terremoti.ingv.it/en/event/" + df["EventID"].astype(str)
df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv", index=False)


#to create empty ROs

ro_research_areas=["Earth sciences"]
ro_creation_mode= "AUTOMATIC"
l=[rohub.ros_create(title="Test", research_areas=ro_research_areas, creation_mode=ro_creation_mode) for i in range(len(df))]

#to write in a seperate file
with open("/Users/sam/Downloads/scenario3B/test_ro.csv", "w") as f:
    write = csv.writer(f)
    write.writerow(l)
with open ("/Users/sam/Downloads/scenario3B/test_ro.csv","r") as file1, open ("/Users/sam/Downloads/scenario3B/test_ro_1.csv","w") as file2:
    content1 = file1.read()
    content2 = content1.replace("Research Object with ID: ", "")
    file2.write(content2)

df = pd.read_csv("/Users/sam/Downloads/scenario3B/test_ro_1.csv")
df = df.T
df.to_csv("/Users/sam/Downloads/scenario3B/test_ro_1.csv")
df = pd.read_csv("/Users/sam/Downloads/scenario3B/test_ro_1.csv")
#header= ["identifier"]
df.to_csv("/Users/sam/Downloads/scenario3B/test_ro_1.csv", header=["identifier"], index=False)
#df = pd.read_csv("/Users/sam/Downloads/scenario3B/test_ro_2.csv")

df = pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
df1= pd.read_csv("/Users/sam/Downloads/scenario3B/test_ro_1.csv", usecols = ['identifier'])
df=df.join(df1['identifier'], how='left')
df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv", index=False)


#automatic update
df = pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
s =list(df["identifier"])
t =list(df["title"])
u =list(df["description"])
v =list(df["Event_url"])
for (x,y,z) in zip(s,t,u):
    rohub.ros_update(identifier=x, title=y, description=z, research_areas = ["Earth sciences"], ros_type="Research Product Research Object")
for (x,y) in zip(s,v):
    rohub.ros_add_external_resource(identifier=x, res_type="Bibliographic Resource", input_url=y, title="Link to the Resource")


#to add folder and folder_id
l1=[rohub.ros_add_folders(identifier=x, name="Impact") for x in s]
df2=pd.DataFrame(l1).rename(columns = {"identifier":"folder_id"})
df = df.join(df2["folder_id"], how='left')

#to add fault line folder
l2=[rohub.ros_add_folders(identifier=x, name="Fault Plane solution") for x in s]
df_l2=pd.DataFrame(l2).rename(columns = {"identifier":"folder_faultplane_id"})
df = df.join(df_l2["folder_faultplane_id"], how='left')

#to add seismicity and hazards
l3=[rohub.ros_add_folders(identifier=x, name="Seismicity and hazards") for x in s]
df_l3=pd.DataFrame(l3).rename(columns = {"identifier":"folder_seismicity_id"})
df = df.join(df_l3["folder_seismicity_id"], how='left')

df["Intensity_Shakemap_url"] = "http://shakemap.ingv.it/shake4/data/"+df["EventID"].astype(str)+"/current/products/intensity.jpg"
df["PGA_url"] = "http://shakemap.ingv.it/shake4/data/"+df["EventID"].astype(str)+"/current/products/pga.jpg"
df["PGV_url"] = "http://shakemap.ingv.it/shake4/data/"+df["EventID"].astype(str)+"/current/products/pgv.jpg"

df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv",index=False)


#to add external resources
Intensity=[rohub.ros_add_external_resource(identifier=x, res_type="Image", input_url=y, title="Intensity Shakemap", folder=z) for (x,y,z) in zip(list(df["identifier"]),list(df["Intensity_Shakemap_url"]),list(df["folder_id"]))]
df3=pd.DataFrame(Intensity).rename(columns = {"identifier":"Intensity_id"})
df = df.join(df3["Intensity_id"], how='left')

PGA=[rohub.ros_add_external_resource(identifier=x, res_type="Image", input_url=y, title="Peak ground acceleration Shakemap", folder=z) for (x,y,z) in zip(list(df["identifier"]),list(df["PGA_url"]),list(df["folder_id"]))]
df4=pd.DataFrame(PGA).rename(columns = {"identifier":"PGA_id"})
df = df.join(df4["PGA_id"], how='left')


PGV=[rohub.ros_add_external_resource(identifier=x, res_type="Image", input_url=y, title="Peak ground velocity Shakemap", folder=z) for (x,y,z) in zip(list(df["identifier"]),list(df["PGV_url"]),list(df["folder_id"]))]
df5=pd.DataFrame(PGV).rename(columns = {"identifier":"PGV_id"})
df = df.join(df5["PGV_id"], how='left')


df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv",index=False)

#To produce geojson and save them and add geoloaction to RO
df = pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
s=list(df["Longitude"])
t=list(df["Latitude"])
w=list(df["EventID"])
u = list(df["identifier"])
os.mkdir("/Users/sam/Downloads/scenario3B/Test_geojson")
for (x,y,z) in zip(s,t,w):
    geojson = {"@context":{"geojson":"https://purl.org/geojson/vocab#"},"type":"Feature","geometry":{"type":"Point","coordinates":[x,y]}}
    with open(f"/Users/sam/Downloads/scenario3B/Test_geojson/{z}.json", "w") as fp:
        json.dump(geojson, fp)

geolocation=[rohub.ros_add_geolocation(identifier=x, body_specification_json=f"/Users/sam/Downloads/scenario3B/Test_geojson/{y}.json") for (x,y) in zip (u,w)]
df6=pd.DataFrame(geolocation).rename(columns = {"identifier":"geolocation_id"})
df = df.join(df6["geolocation_id"], how='left')
df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv",index=False)

#to generate sketch pngs
os.mkdir("/Users/sam/Downloads/scenario3B/Test_sketch")
df= pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
s=list(df["Latitude"])
t=list(df["Longitude"])
u=list(df["EventID"])
for (x,y,z) in zip(s,t,u):
    fig = px.scatter_geo(df,lat=[x],lon=[y])
    fig.update_traces(marker=dict(size=20))
    #fig.show()
    fig.write_image(f"/Users/sam/Downloads/scenario3B/Test_sketch/{z}.png")

#to add sketch
df =pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
s=list(df["identifier"])
t=list(df["EventID"])
sketch=[rohub.ros_add_internal_resource(identifier=x, res_type="Sketch", file_path=f"/Users/sam/Downloads/scenario3B/Test_sketch/{y}.png") for (x,y) in zip(s,t)]
df2=pd.DataFrame(sketch).rename(columns = {"identifier":"sketch_id"})
df = df.join(df2["sketch_id"], how='left')
df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv",index=False)

#Adding annotations and keywords
df =pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
keyword_annotation = [rohub.ros_add_annotations(identifier=x) for x in list(df["identifier"])]
df_annotation=pd.DataFrame(keyword_annotation).rename(columns = {"identifier":"keyword_annotation_id"})
df = df.join(df_annotation["keyword_annotation_id"], how='left')
df.to_csv("/Users/sam/Downloads/scenario3B/ro_create.csv",index=False)

df= pd.read_csv("/Users/sam/Downloads/scenario3B/ro_create.csv")
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="Earthquake", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="Seismic activity", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="earthquake impact", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]

#os.remove("/Users/sam/Downloads/scenario3B/test.txt")
os.remove("/Users/sam/Downloads/scenario3B/test.csv")
os.remove("/Users/sam/Downloads/scenario3B/test_1.csv")
os.remove("/Users/sam/Downloads/scenario3B/test_ro.csv")
os.remove("/Users/sam/Downloads/scenario3B/test_ro_1.csv")
