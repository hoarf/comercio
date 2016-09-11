def read_api_keys():
    with open(API_FILE, 'r') as f:
        yield f.read().rstrip()

def read_saved_data():
    if os.path.exists(LOC_FILE):
        return pd.read_csv(LOC_FILE,index_col=0)
    else:
        return pd.read_fwf(DATA_FILE, encoding='ISO-8859-1')

def geolocate(addr, geolocators):
    try:
        random_locator = np.random.choice(geolocators)
        return random_locator.geocode("Porto Alegre %s" % addr)[1]
    except TypeError:
        print("Não pode geolocalizar: %s" % x)
        return (None, None)
    except NameError:
        print("Timeout %s" % addr)
        return (None, None)
    except geopy.exc.GeocoderTimedOut:
        print("Timeout %s" % addr)
        return (None, None)

data = read_saved_data()

if not "Latitude" in data:
    data = pd.DataFrame(data["Endereço"].dropna())
    data["Latitude"] = np.NaN
    data["Longitude"] = np.NaN

geolocators = [ GoogleV3(x) for x in read_api_keys() ]

locate_dict = data.drop_duplicates().to_dict(orient='records')

print("Localized: %s" % (data[data["Latitude"].notnull()].size/data.size))
print("Updating known localizations...")
try:
    for d in locate_dict:
        if np.isnan(d["Latitude"]):
            result = geolocate(d["Endereço"], geolocators)
            d["Latitude"], d["Longitude"] = result

except Exception as e:
    print(e)

data.update(pd.DataFrame(locate_dict))
print("New localized amount: %s" % (data[data["Latitude"].notnull()].size/data.size))


data[["Endereço","Latitude","Longitude"]].to_csv(LOC_FILE)
