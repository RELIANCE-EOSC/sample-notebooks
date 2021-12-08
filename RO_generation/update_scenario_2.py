import os
from rohub import rohub, settings
import pandas as pd
import csv
import urllib.request
import json


rohub.login(username="rpalma", password="gato_domestico")


os.mkdir("/Users/sam/Downloads/scenario2")
url = "http://193.206.223.51/rest/reports/"
urllib.request.urlretrieve(url,"/Users/sam/Downloads/scenario2/test.json")

#to read the json to csv
df = pd.read_json("/Users/sam/Downloads/scenario2/test.json")
df.to_csv("/Users/sam/Downloads/scenario2/ro_create.csv", index=False)

#to create template csv
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
df["Location"]= df["file_pdf"].str.extract('([A-Z]\w{0,})')
df["Location"]= df["Location"].str.replace("\d", "")
df["Location"]= df["Location"].str[10:]
df["Location"]=df["Location"].replace({"GiornalieroStromboli":"Stromboli", "Etna":"Mt. Etna"}, regex=True)

df["date"] = df["date_publication"].astype('datetime64[ns]').astype(str)
df["date"]=[x[:-8] for x in df['date']]

df["title"] = df["Location"]+" (Italy) multidisciplinary weekly report generated on "+df["date"]
df["description"]= "This Research Object provides the weekly multidisciplinary report generated at "+df["date_publication"].astype('datetime64[ns]').astype(str)+" and relative to the previous week, on the volcanic activity of "+df["Location"]+" (Italy) from the monitoring networks managed by INGV (Istituto Nazionale di Geofisica e Vulcanologia, Italy). INGV provides the reports in convention regime with the Italian Civil Protection Department. The report is in Italian."
df.to_csv("/Users/sam/Downloads/scenario2/ro_create.csv", index=False)


#to create empty ROs
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
ro_research_areas=["Earth sciences"]
ro_creation_mode = "AUTOMATIC"
l=[rohub.ros_create(title="Test", research_areas=ro_research_areas, creation_mode=ro_creation_mode) for i in range(len(df))]

#to write in a seperate file
with open("/Users/sam/Downloads/scenario2/test_ro.csv", "w") as f:
    write = csv.writer(f)
    write.writerow(l)
with open ("/Users/sam/Downloads/scenario2/test_ro.csv","r") as file1, open ("/Users/sam/Downloads/scenario2/test_ro_1.csv","w") as file2:
    content1 = file1.read()
    content2 = content1.replace("Research Object with ID: ", "")
    file2.write(content2)
#making dataframe with identifiers
df = pd.read_csv("/Users/sam/Downloads/scenario2/test_ro_1.csv")
df = df.T
df.to_csv("/Users/sam/Downloads/scenario2/test_ro_1.csv")
df = pd.read_csv("/Users/sam/Downloads/scenario2/test_ro_1.csv")
df.to_csv("/Users/sam/Downloads/scenario2/test_ro_1.csv", header=["identifier"], index=False)

df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
df1= pd.read_csv("/Users/sam/Downloads/scenario2/test_ro_1.csv", usecols = ['identifier'])
df=df.join(df1['identifier'], how='left')
df.to_csv("/Users/sam/Downloads/scenario2/ro_create.csv", index=False)

#to update ROs
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
s =list(df["identifier"])
t =list(df["title"])
u =list(df["description"])
v =list(df["url_pdf"])
for (x,y,z) in zip(s,t,u):
    rohub.ros_update(identifier=x, title=y, description=z, research_areas = ["Earth sciences"], ros_type="Bibliographic Research Object")

#External resources
for (x,y) in zip(s,v):
    rohub.ros_add_external_resource(identifier=x, res_type="Bibliographic Resource", input_url=y, title="Link to the Weekly Report")

#to add disclaimer internally
urllib.request.urlretrieve("https://box.psnc.pl/f/c224999833/?raw=1","/Users/sam/Downloads/scenario2/INGV_disclaimer.pdf")
Disclaimer=[rohub.ros_add_internal_resource(identifier=x, res_type="Document", file_path="/Users/sam/Downloads/scenario2/INGV_disclaimer.pdf", title="Disclaimer INGV") for x in list(df["identifier"])]
df2=pd.DataFrame(Disclaimer).rename(columns = {"identifier":"Disclaimer_res_id"})
df = df.join(df2["Disclaimer_res_id"], how='left')
df.to_csv("/Users/sam/Downloads/scenario2/ro_create.csv", index=False)

#sketch_url="http://sandbox.rohub.org/rodl/ROs/Etna_bulletin_20210607_20210613/etna_sketch.png"
#urllib.request.urlretrieve(sketch_url,"/Users/sam/Downloads/scenario2/Etna_sketch.png")

#Sketch and geolocation only for Etna
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
df_etna=df.loc[df['Location'] == 'Mt. Etna']
urllib.request.urlretrieve("https://box.psnc.pl/f/2fd83e2ddd/?raw=1","/Users/sam/Downloads/scenario2/etna_sketch.png")
[rohub.ros_add_internal_resource(identifier=x, res_type="Sketch", file_path="/Users/sam/Downloads/scenario2/etna_sketch.png", title="Etna Sketch") for x in list(df_etna["identifier"])]

urllib.request.urlretrieve("https://box.psnc.pl/f/8bb9f0fff7/?raw=1","/Users/sam/Downloads/scenario2/etna.json")
[rohub.ros_add_geolocation(identifier=x, body_specification_json="/Users/sam/Downloads/scenario2/etna.json") for x in list(df_etna["identifier"])]

#sketch and geolocation only for Stromboli
df_stromboli=df.loc[df['Location'] == 'Stromboli']

urllib.request.urlretrieve("https://box.psnc.pl/f/bb6f127aa2/?raw=1","/Users/sam/Downloads/scenario2/stromboli_sketch.png")
[rohub.ros_add_internal_resource(identifier=x, res_type="Sketch", file_path="/Users/sam/Downloads/scenario2/stromboli_sketch.png", title="Stromboli Sketch") for x in list(df_stromboli["identifier"])]


urllib.request.urlretrieve("https://box.psnc.pl/f/af7c401dcc/?raw=1","/Users/sam/Downloads/scenario2/stromboli.json")
[rohub.ros_add_geolocation(identifier=x, body_specification_json="/Users/sam/Downloads/scenario2/stromboli.json") for x in list(df_stromboli["identifier"])]

#Adding annotations and keywords
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
keyword_annotation = [rohub.ros_add_annotations(identifier=x) for x in list(df["identifier"])]
df_annotation=pd.DataFrame(keyword_annotation).rename(columns = {"identifier":"keyword_annotation_id"})
df = df.join(df_annotation["keyword_annotation_id"], how='left')
df.to_csv("/Users/sam/Downloads/scenario2/ro_create.csv", index=False)

#to add keyword triples
#keywords=["GPS","Geochemistry", "Levelling", "Monitoring Networks", "Weekly Reports", "Degassing","Seismicity"]
df = pd.read_csv("/Users/sam/Downloads/scenario2/ro_create.csv")
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="GPS", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="Weekly Seismicity Report", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="Degassing", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
[rohub.ros_add_triple(the_subject=f"https://w3id.org/ro-id/{x}", the_predicate="http://swrc.ontoware.org/ontology#keywords", the_object="Monitoring Networks", annotation_id=z) for (x,z) in zip(list(df["identifier"]),list(df["keyword_annotation_id"]))]
#remove unwanted files
os.remove("/Users/sam/Downloads/scenario2/test_ro_1.csv")
os.remove("/Users/sam/Downloads/scenario2/test_ro.csv")
