from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Region, Base, Wine, User

engine = create_engine('sqlite:///winecatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a dummy user 
User1 = User(name='Wino Dino', email='winesucks@terroir.com', picture='https://i.imgur.com/OXDj7nJ.jpg')
session.add(User1)
session.commit()

# Create Burgundy Region
region1 = Region(user_id=1, name='Burgundy')
session.add(region1)
session.commit()

# Create Wines for Burgundy
wine1 = Wine(user_id=1, name='Goisot Aligote 2017', 
             description='This is a fine Aligote, unoaked and aged on the lees. It will absolutely keep for several years to come.', 
             price='$18.96', region=region1)
session.add(wine1)
session.commit()

wine2 = Wine(user_id=1, name='Lapiere Raisins Gauloins 2018',
             description='A simple Vin de France with lovely, fresh, grapey Gamay fruit. This joyous, refreshing, and lively wine is made by the son of Marcel Lapierre.',
             price='$15.99', region=region1)
session.add(wine2)
session.commit()

wine3 = Wine(user_id=1, name='Clos de la Roilette Fleurie 2014',
             description='Elegant black cherry fruit flavors, hints of minerals and violets, and a meaty structure. Try with grilled foods and soft cheeses.',
             price='$19.99', region=region1)
session.add(wine3)
session.commit()

# Create Champagne Region
region2 = Region(user_id=1, name='Champagne')
session.add(region2)
session.commit()

# Create Wines for Champagne
wine1 = Wine(user_id=1, name='Bereche Le Cran 2007',
             description='Champagne showcases austere minerality and ever-lasting complexity.',
             price='$149.96', region=region2)
session.add(wine1)
session.commit()

wine2 = Wine(user_id=1, name='Benoit Lahaye, Brut Nature NV',
             description='Lahaye\'s Brut Nature is a fine example of the clarity one can achieve in non-dosage Champagne.',
             price='$68.99', region=region2)
session.add(wine2)
session.commit()

wine3 = Wine(user_id=1, name='Dom Perignon Rose 2005',
             description='Floral notes mingle with a sensation of dried red berries with chalky minerality.',
             price='$312.96', region=region2)
session.add(wine3)
session.commit()

# Create California Region
region3 = Region(user_id=1, name='California')
session.add(region3)
session.commit()

# Create Wines for California
wine1 = Wine(user_id=1, name='Arnot Roberts Gamay El Dorado 2017',
             description='This Gamay shows great purity of fruit and lets the terroir speak for itself.',
             price='$34.96', region=region3)
session.add(wine1)
session.commit()

wine2 = Wine(user_id=1, name='Bacchus Cabernet Sauvignon 2017',
             description='Bright and approachable, this is an easy-drinking Cabernet Sauvignon with balanced flavors of cassis, black plum, black currants, and a touch of cedar.',
             price='$9.99', region=region3)
session.add(wine2)
session.commit()

wine3 = Wine(user_id=1, name='Broc Cellars Love Red 2017',
             description='Made to be light and quaffable, it\'s a delicious thirst quencher. Even better when it\'s slightly chilled.',
             price='$19.96', region=region3)
session.add(wine3)
session.commit()

print('added regions and wines!')


