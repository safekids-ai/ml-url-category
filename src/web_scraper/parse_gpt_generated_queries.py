import pandas as pd
import requests
from tqdm import tqdm
import requests
import json

#google detects parsers easily, so I found that using serper.dev api was the easiest way to send many queries to google.
#it gives 2500 tokens for free, which is more than sufficient.


def search_google(phrase):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": phrase,
    "num": 100
    })
    headers = {
    'X-API-KEY': 'YOUR SERPER API KEY',
    'Content-Type': 'application/json'
    }
    r = requests.request("POST", url, headers=headers, data=payload)
    return r

google_queries={
'adult_sexual_content':["XXX videos"
    ,"adult sites"
    ,"nude webcam chat"
    ,"pornography websites"
    ,"erotic stories"
    ,"NSFW images"
    ,"explicit content"
    ,"adult film stars"
    ,"voyeur sites"
    ,"sexy video clips"
    ,"swinger clubs"
    ,"BDSM content"
    ,"lingerie models"
    ,"adult webcam models"
    ,"strip clubs near me"
    ,"sex toy shops"
    ,"adult video stores"
    ,"amateur adult videos"
    ,"nude celeb photos"
    ,"explicit dating apps"],
'body_image/related_to_disordered_eating':["how to lose weight fast"
    ,"skinny diet tips"
    ,"thinspo"
    ,"pro-ana tips"
    ,"laxative weight loss"
    ,"fasting for weight loss"
    ,"calorie counting apps"
    ,"extreme diets"
    ,"how to be skinny"
    ,"low BMI"
    ,"exercise for weight loss"
    ,"how to look thin"
    ,"body dysmorphia symptoms"
    ,"weight loss surgery"
    ,"lose 10 pounds in a week"
    ,"waist training"
    ,"extreme workout routines"
    ,"low-calorie foods"
    ,"no-carb diets"
    ,"get a thigh gap"],
'clothing_fashion_and_jewelry':["latest fashion trends 2023"
    ,"best jewelry brands"
    ,"cheap designer clothes"
    ,"top 10 luxury handbags"
    ,"street style outfits"
    ,"how to dress like a celebrity"
    ,"sustainable fashion brands"
    ,"online fashion stores"
    ,"best watches for men"
    ,"summer outfits ideas"
    ,"vintage clothing stores"
    ,"bridal jewelry sets"
    ,"fashion week highlights"
    ,"high heels collection"
    ,"designer eyeglasses"
    ,"winter coats for women"
    ,"latest shoe trends"
    ,"men's casual fashion"
    ,"affordable engagement rings"
    ,"leather jacket styles"
    ],
'criminal/malicious':["how to hack Facebook account"
    ,"illegal torrent sites"
    ,"credit card fraud methods"
    ,"buy fake ID online"
    ,"how to pick a lock"
    ,"dark web marketplaces"
    ,"illegal drug trade"
    ,"stolen credit card numbers"
    ,"pirated software downloads"
    ,"how to break into a house"
    ,"anarchist cookbook recipes"
    ,"how to make fake money"
    ,"hack Instagram password"
    ,"GPS jammer for sale"
    ,"car theft techniques"
    ,"illegal weapon sales"
    ,"black hat hacking forums"
    ,"how to evade the police"
    ,"counterfeit goods online"
    ,"download movies illegally"],
'drugs_alcohol_or_tobacco_related':["how to make a homemade bong"
    ,"buy cigarettes online"
    ,"best tequila brands"
    ,"where to buy marijuana"
    ,"psychedelic mushrooms identification"
    ,"types of recreational drugs"
    ,"homebrewing alcohol"
    ,"smoking paraphernalia"
    ,"buy vape juice online"
    ,"how to roll a joint"
    ,"illegal drug effects"
    ,"liquor store near me"
    ,"tobacco shops"
    ,"mixing alcohol and drugs"
    ,"over-the-counter highs"
    ,"drug testing kits"
    ,"how to make moonshine"
    ,"best cigars"
    ,"opiate alternatives"
    ,"DIY e-liquid recipes"],
'entertainment_news_and_streaming':["latest Hollywood gossip"
    ,"watch free movies online"
    ,"Netflix top 10 series"
    ,"celebrity breakups 2023"
    ,"upcoming movie trailers"
    ,"best TV shows to binge"
    ,"how to stream live sports"
    ,"award show highlights"
    ,"latest music releases"
    ,"top box office hits"
    ,"reality TV show auditions"
    ,"popular YouTube vloggers"
    ,"watch live concerts online"
    ,"celebrity interviews"
    ,"movie reviews and ratings"
    ,"streaming service comparisons"
    ,"Disney+ new releases"
    ,"video game reviews"
    ,"best podcasts this week"
    ,"top-rated Netflix documentaries"],
'fake_news':["moon landing hoax"
    ,"5G causes COVID"
    ,"world is flat proof"
    ,"vaccines cause autism"
    ,"chemtrails and mind control"
    ,"alien abductions evidence"
    ,"Illuminati confirmed"
    ,"government mind control techniques"
    ,"Bigfoot sightings"
    ,"Elvis Presley alive"
    ,"deep state conspiracy"
    ,"HAARP weather control"
    ,"New World Order plans"
    ,"COVID-19 is a hoax"
    ,"fake news about climate change"
    ,"holocaust denial"
    ,"celebrity death hoaxes"
    ,"false flag attacks"
    ,"Area 51 secrets"
    ,"fake cure for cancer"],
'gambling': ["online poker real money"
    ,"best betting sites"
    ,"how to win at slots"
    ,"sports betting tips"
    ,"casino bonus codes"
    ,"lottery ticket online"
    ,"blackjack strategies"
    ,"horse racing odds"
    ,"roulette tips"
    ,"gambling addiction help"
    ,"daily fantasy sports"
    ,"bingo games online"
    ,"craps tutorial"
    ,"poker tournament schedule"
    ,"high-stakes gambling"
    ,"slot machine tricks"
    ,"understanding odds"
    ,"gambling laws"
    ,"play casino games online"
    ,"best poker players"],
'hate_speech': [
    "racial slurs"
    ,"hate groups"
    ,"discriminatory jokes"
    ,"white supremacy forums"
    ,"anti-Semitic comments"
    ,"homophobic slurs"
    ,"xenophobic rhetoric"
    ,"anti-immigrant blogs"
    ,"gender-based insults"
    ,"religious discrimination"
    ,"inciting violence"
    ,"ethnic stereotypes"
    ,"hate speech laws"
    ,"offensive memes"
    ,"bigoted opinions"
    ,"cyberbullying tips"
    ,"hate crimes statistics"
    ,"alt-right websites"
    ,"misogynistic comments"
    ,"prejudiced language"
],
'online_gaming': [
    "best multiplayer games 2023"
    ,"how to cheat in online games"
    ,"Fortnite skins"
    ,"gaming forums"
    ,"best RPGs of all time"
    ,"eSports tournaments"
    ,"mobile gaming apps"
    ,"Minecraft mods"
    ,"video game cheats"
    ,"Steam sale dates"
    ,"gaming live streams"
    ,"console vs PC debate"
    ,"game hacks and exploits"
    ,"upcoming video game releases"
    ,"top Twitch streamers"
    ,"video game reviews"
    ,"buy in-game currency"
    ,"MMORPG free trials"
    ,"gaming accessories"
    ,"game emulators for PC"
],
'self_harm/suicidal_content': [
    "how to self-harm"
    ,"methods of suicide"
    ,"pain-free suicide"
    ,"cutting techniques"
    ,"how to tie a noose"
    ,"overdose on pills"
    ,"ending it all"
    ,"easiest way to die"
    ,"self-harm coping methods"
    ,"jumping off a building"
    ,"suicidal ideation"
    ,"self-injury tools"
    ,"suicide notes examples"
    ,"ways to harm yourself"
    ,"asphyxiation methods"
    ,"how to overdose"
    ,"self-harm forums"
    ,"dealing with depression alone"
    ,"how to commit suicide"
    ,"feeling worthless"
],
'sex_education': ["how do contraceptives work"
    ,"sexual anatomy diagram"
    ,"safe sex practices"
    ,"STD symptoms and treatment"
    ,"how to use a condom"
    ,"menstrual cycle explained"
    ,"sexual orientation definitions"
    ,"birth control options"
    ,"reproductive health"
    ,"early signs of pregnancy"
    ,"consent in relationships"
    ,"sexual positions for pregnancy"
    ,"effects of hormonal imbalance"
    ,"sexual health clinics"
    ,"symptoms of yeast infection"
    ,"plan B pills"
    ,"how to do a self breast-exam"
    ,"what is HPV"
    ,"fertility treatments"
    ,"understanding gender identity"
],
'shopping_and_product_reviews': [
    "best smartphones 2023"
    ,"Amazon daily deals"
    ,"makeup product reviews"
    ,"how to save money on groceries"
    ,"top 10 laptops"
    ,"unboxing videos"
    ,"luxury car comparisons"
    ,"discount codes for online shopping"
    ,"best skincare brands"
    ,"kitchen appliance ratings"
    ,"Black Friday sales"
    ,"book reviews and recommendations"
    ,"top gadgets for men"
    ,"furniture store reviews"
    ,"best online boutiques"
    ,"sustainable products"
    ,"latest tech reviews"
    ,"kids toys bestsellers"
    ,"compare flight prices"
    ,"top-rated vacuum cleaners"
],
'social_media_and_chat': ["how to get more Instagram followers"
    ,"best Snapchat filters"
    ,"Facebook privacy settings"
    ,"most popular TikTok challenges"
    ,"Twitter trending topics"
    ,"WhatsApp tricks"
    ,"social media influencers"
    ,"best Discord servers"
    ,"LinkedIn networking tips"
    ,"how to go viral"
    ,"Reddit subreddits list"
    ,"YouTube channel ideas"
    ,"Telegram bots"
    ,"Clubhouse rooms"
    ,"how to monetize social media"
    ,"virtual chat rooms"
    ,"social media addiction"
    ,"Instagram Reels tips"
    ,"Twitter threads worth reading"
    ,"how to create a meme"
],
'violence': [
    "violent crime videos"
    ,"fighting techniques"
    ,"extreme sports injuries"
    ,"gang violence statistics"
    ,"real-life horror stories"
    ,"riot footage"
    ,"war zone photography"
    ,"best action movies"
    ,"boxing knockouts"
    ,"military combat videos"
    ,"violent video games"
    ,"brutal street fights"
    ,"how to make a Molotov cocktail"
    ,"mass shooting news"
    ,"torture methods"
    ,"police brutality cases"
    ,"domestic violence help"
    ,"UFC highlights"
    ,"animal cruelty videos"
    ,"graphic accident footage"
],
'weapons': [ "how to make a homemade bomb"
    ,"best guns for self-defense"
    ,"knife throwing techniques"
    ,"military-grade weapons"
    ,"buy firearms online"
    ,"types of explosives"
    ,"black market weapons"
    ,"concealed carry permit"
    ,"archery tips"
    ,"tasers and stun guns"
    ,"how to clean a gun"
    ,"pepper spray effectiveness"
    ,"swords and daggers"
    ,"firearm safety courses"
    ,"lethal weapons"
    ,"ammo types and uses"
    ,"nuclear weapons news"
    ,"non-lethal self-defense"
    ,"best hunting rifles"
    ,"how to disarm someone"
],
'safe': [
    "homemade cookie recipes"
    ,"family vacation spots"
    ,"best books for kids"
    ,"easy science experiments"
    ,"educational games online"
    ,"how to plant a garden"
    ,"pet care tips"
    ,"yoga for beginners"
    ,"kids' crafts ideas"
    ,"healthy meal plans"
    ,"how to knit a scarf"
    ,"learning a new language"
    ,"DIY home decor"
    ,"solar system facts"
    ,"how to build a birdhouse"
    ,"family board games"
    ,"best animated movies"
    ,"exercise routines"
    ,"recycling tips"
    ,"museum virtual tours"
    'Animal facts'
    ,'Fairy tales and childrens stories'
    ,'History of art'
    ,'Geography quizzes'
    ,'Space and astronomy'
    ,'Famous inventors and their inventions'
    ,'Kids cooking recipes'
    ,'Learning musical instruments'
    ,'Childrens poetry'
    ,'Math games and puzzles'
    ,'Classic literature for children'
    ,'Simple DIY science experiments'
    ,'Renewable energy sources'
    ,'Oceanography and marine life'
    ,'Lessons on friendship and kindness'
    ,'Animated movie reviews'
    ,'Nature hikes and outdoor activities'
    ,'Famous landmarks and wonders of the world'
    ,'Multicultural festivals'
    ,'Learning about different professions'
    ,"balanced diet for children"
    ,"importance of body positivity"
    ,"healthy eating habits"
    ,"history of traditional clothing"
    ,"cultural significance of attire"
    ,"textile history and techniques"
    ,"cybersecurity tips"
    ,"how to prevent burglary"
    ,"self-defense legal guidelines"
    ,"quitting smoking methods"
    ,"drug addiction recovery stories"
    ,"alcohol detox procedures"
    ,"BBC World News"
    ,"CNN Breaking News"
    ,"National Geographic documentaries"
    ,"News websites"
    ,"basic budgeting tips"
    ,"how to save money"
    ,"personal finance guidelines"
    ,"diversity training programs"
    ,"importance of inclusion"
    ,"combating racism and prejudice"
    ,"age-appropriate books for kids"
    ,"educational cartoons"
    ,"child-friendly news sources"
    ,"Scratch coding for kids"
    ,"educational video games"
    ,"mental health helplines"
    ,"counseling services"
    ,"positive coping mechanisms"
    ,"basic biology lessons for kids"
    ,"understanding the human body"
    ,"age-appropriate health education"
    ,"sustainable shopping guide"
    ,"ethical consumerism tips"
    ,"eco-friendly products"
    ,"Khan Academy forums"
    ,"educational podcasts for kids"
    ,"safe chat rooms for learning"
    ,"conflict resolution techniques"
    ,"history of peace movements"
    ,"anger management resources"
    ,"history of medieval armor"
    ,"ancient weapon techniques"
    ,"museum exhibits on armory"
    'simple science experiments for kids',
    'how does photosynthesis work',
    'what is gravity',
    'types of clouds for kids',
    'basic chemistry for kids',
    'how do magnets work',
    'water cycle explanation',
    'why is the sky blue',
    'earth layers for kids',
    'human body systems for kids',
    'basic math games for kids',
    'learn multiplication tables',
    'fun geometry shapes',
    'how to do long division',
    'counting money for kids',
    'simple fractions for kids',
    'math puzzles for children',
    'math word problems for kids',
    'times tables songs',
    'place value games',
    'famous historical figures for kids',
    'Egyptian pyramids history',
    'timeline of World War 2 for kids',
    'who was George Washington',
    'history of the Olympics',
    'medieval castles history',
    'history of airplanes',
    'American Revolution for kids',
    'ancient Rome for kids',
    'Civil Rights Movement for kids',
    'easy DIY crafts for kids',
    'how to draw a cat',
    'paper airplane designs',
    'homemade playdough recipe',
    'coloring pages for kids',
    'how to make slime',
    'origami for beginners',
    'painting techniques for kids',
    'make your own friendship bracelets',
    'how to weave a basket',
    'best children’s books',
    'how to write a poem for kids',
    'famous fairy tales',
    'reading comprehension exercises for kids',
    'classic literature for children',
    'young adult novels list',
    'rhyming words game',
    'short stories for kids',
    'book report template',
    'learn to read apps for kids',
    'world map for kids',
    'capital cities quiz',
    'continents and oceans',
    'types of landforms',
    'famous landmarks for kids',
    'geography games for kids',
    'climate zones explanation',
    'how to read a map',
    'geography trivia for kids',
    'what is latitude and longitude',
    'learn to play the guitar for kids',
    'basic music theory for kids',
    'famous composers for children',
    'best kids songs playlist',
    'how to read sheet music',
    'musical instruments names and pictures',
    'rhythm exercises for kids',
    'music genres list',
    'singing lessons for children',
    'history of music for kids',
    'learn Spanish for kids',
    'basic French phrases',
    'English grammar for kids',
    'Japanese for beginners',
    'sign language basics',
    'common Italian words',
    'Russian alphabet for kids',
    'Chinese characters for beginners',
    'learn to write cursive',
    'vocabulary games for kids',
    'easy yoga poses for kids',
    'healthy snacks for kids',
    'how to do a cartwheel',
    'basic soccer skills',
    'importance of exercise for kids',
    'how to tie shoelaces',
    'dental hygiene for kids',
    'kids workout routine',
    'fun outdoor games',
    'first aid basics for kids',
    'phases of the moon for kids',
    'what is a solar eclipse',
    'how do telescopes work',
    'facts about planets',
    'constellations for kids',
    'history of astronomy for kids',
    'what is a shooting star',
    'space missions for kids',
    'how to use a star map',
    'what is a black hole',
    'types of animals for kids',
    'how do plants grow',
    'bird watching for kids',
    'endangered species for children',
    'how to go camping',
    'ocean animals list',
    'forest ecosystem for kids',
    'how to identify trees',
    'butterfly life cycle for kids',
    'facts about dinosaurs',
    'easy cookie recipes for kids',
    'how to make pancakes',
    'fruit smoothie recipes',
    'baking basics for kids',
    'how to make a sandwich',
    'healthy lunch ideas for kids',
    'make your own pizza',
    'measuring ingredients for baking',
    'decorating cupcakes',
    'kitchen safety for kids',
    'introduction to coding for kids',
    'how to use a computer',
    'safe browsing tips for kids',
    'basic HTML for beginners',
    'how to make a video game',
    'types of software',
    'what is the internet',
    'learn to type for kids',
    'what is a robot',
    'how to create a website',
    'what is democracy',
    'how do elections work',
    'world religions for kids',
    'what is economics',
    'basic laws and rights',
    'how does government work',
    'what is culture',
    'what are social norms',
    'community helpers list',
    'different types of families',
    'how to recycle for kids',
    'what is global warming',
    'why is conservation important',
    'types of renewable energy',
    'how to save water',
    'endangered animals list',
    'effects of pollution',
    'how to make a compost',
    'what is an ecosystem',
    'why are bees important'
]
}

for idx,(k,v) in tqdm(enumerate(google_queries.items())):
    cat_dfs = []
    for phrase in v:
        r = search_google(phrase)
        df = pd.DataFrame(eval(r.content)['organic'])[['title','link','snippet']]
        df['category'] = k
        df['query']= phrase
        cat_dfs.append(df)
    cat_unif = pd.concat(cat_dfs)
    cat_unif.to_parquet(f'data_preparation/google_queries/cat_{idx}.parquet')


df = pd.read_parquet('data_preparation/google_queries/')