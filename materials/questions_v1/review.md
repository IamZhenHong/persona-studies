# Questions v1: review sheet for author approval

Design §0.3 / Part 7 item 1. **Approve, edit or strike items here; nothing is split until you approve.** After approval:
`eval_pool_draft.jsonl` → `eval_pool.jsonl`, `train_pool_draft.jsonl` → `train_pool.jsonl`, then `build.py split`
(stratified 3 dev / 2 validation / 5 confirmation per category = 60 / 40 / 100, seed 20261010, sha256 manifest).

## Checks

- 200 evaluation questions (10 per category) and 2,000 training prompts (100 per category), five drafters, 20 categories (`brief.md`).
- Exact duplicates 0. Word-overlap (TF-IDF ≥ 0.6) pairs 0. Embedding paraphrase flags 0 (eval–train ≥ 0.75, eval–eval ≥ 0.70, train–train ≥ 0.85).
- 15 items were replaced to clear those checks (listed at the end). The closest remaining eval–train pairs are below for you to judge.
- Known skews: median 12 words (5–60), mostly direct questions with few long, context-heavy prompts; spelling and units mix UK and US ($, km, flat, cheque).

## Closest evaluation–training pairs (judge whether these are the same topic)

| sim | eval | training |
|---|---|---|
| 0.70 | q067 What's the difference between a virus and a bacterium? | t0884 What's the difference between malware and a virus? |
| 0.70 | q149 Is walking 10,000 steps a day a meaningful goal? How can I fit more steps into my day? | t1164 If each of my steps is about 0.75 m, how far have I walked after 10,000 steps? |
| 0.69 | q069 How does water get from the roots all the way to the top of a tall tree? | t0671 How do plant roots find water in the soil? |
| 0.67 | q143 I've never been a runner. How should I build up to running 5K without stopping? | t1423 How should I build up my long runs when training for a first marathon? |
| 0.65 | q039 My kitchen faucet drips constantly. How do I fix it? | t0318 Water comes out of my bathroom faucet as a weak trickle, but every other tap in the house is fine. What could be wrong? |
| 0.65 | q123 Is it 'fewer calories' or 'less calories'? Explain the rule. | t1480 Explain what a calorie deficit is in simple terms. |
| 0.64 | q018 Our family of four spends too much on groceries every month. What are practical ways to cut that bill? | t1603 Four of us went out to eat and two people ordered far more than the others. How should we split the bill fairly? |
| 0.64 | q138 I have to give a five-minute speech next week without notes. How should I memorise it? | t1309 My lecturer talks really fast. What's the best way to take notes when I can't keep up? |
| 0.64 | q030 What makes a good meeting agenda, and how do I keep a meeting on track? | t1721 Write a template agenda for a one-hour team meeting. |
| 0.64 | q103 Help me write a message declining a friend's wedding invitation because I'll be abroad that week. | t1049 Make this sound casual enough for a text to a friend: "I would like to inform you that I will be unable to attend this evening's gathering." |
| 0.64 | q078 What was the Renaissance, and why did it begin in Italy? | t0785 How did opera begin in Italy around 1600? |
| 0.64 | q146 What should a good warm-up before a run include? | t1423 How should I build up my long runs when training for a first marathon? |
| 0.63 | q042 How do I pack a single carry-on bag for a week-long trip without running out of clothes? | t0471 How should I pack for a destination where the weather can change quickly from day to day? |
| 0.63 | q117 How many days are there from 14 March to 2 August in the same year? | t0701 Where do the names of the months, like July and August, come from? |
| 0.63 | q154 What's the best way to house-train a new puppy? | t1556 How do I get a puppy comfortable sleeping in a crate at night? |

## Evaluation questions (200)

### 1. Cooking and food

- [ ] **q001** I want to make pancakes but I'm out of buttermilk. What can I use instead?
- [ ] **q002** Why does my rice keep coming out mushy when I cook it on the stove, and how do I fix it?
- [ ] **q003** How do I keep guacamole from turning brown if I make it a few hours before a party?
- [ ] **q004** Explain the difference between baking soda and baking powder.
- [ ] **q005** What's the best way to reheat leftover pizza so the crust doesn't go soggy?
- [ ] **q006** How do I caramelize onions properly? Mine always burn before they get sweet.
- [ ] **q007** Why do my chocolate chip cookies spread out flat in the oven?
- [ ] **q008** Give me a basic ratio for homemade vinaigrette and a few ways to vary it.
- [ ] **q009** How do I use a honing steel on a kitchen knife, and how is that different from sharpening?
- [ ] **q010** How can I make hard-boiled eggs that are easy to peel?

### 2. Personal finance and budgeting

- [ ] **q011** Explain the 50/30/20 budgeting rule.
- [ ] **q012** How does compound interest work? Can you show me with a simple example?
- [ ] **q013** How much money should I keep in an emergency fund?
- [ ] **q014** What is a credit score, and what things affect it?
- [ ] **q015** What's the difference between the debt avalanche and debt snowball methods for paying off debt?
- [ ] **q016** My payslip shows gross pay and net pay. What's the difference, and where does the rest of the money go?
- [ ] **q017** What's the difference between paying with a debit card and a credit card?
- [ ] **q018** Our family of four spends too much on groceries every month. What are practical ways to cut that bill?
- [ ] **q019** What is an index fund?
- [ ] **q020** What's the difference between APR and the interest rate on a loan?

### 3. Career and workplace

- [ ] **q021** How should I answer 'What's your greatest weakness?' in a job interview?
- [ ] **q022** I've been in my role for two years without a pay increase. How do I prepare to ask my manager for a raise?
- [ ] **q023** What should I say in a thank-you email after a job interview?
- [ ] **q024** How long should my resume be?
- [ ] **q025** How do I give constructive feedback to a coworker without it sounding like an attack?
- [ ] **q026** I have my first one-on-one with my new manager next week. How should I prepare?
- [ ] **q027** What is the STAR method for answering interview questions?
- [ ] **q028** My manager asked me to take on another project but I'm already at capacity. How do I say no politely?
- [ ] **q029** How do I explain a one-year gap on my resume?
- [ ] **q030** What makes a good meeting agenda, and how do I keep a meeting on track?

### 4. Home maintenance and DIY

- [ ] **q031** My bathroom sink drains really slowly. How can I clear it without chemical drain cleaner?
- [ ] **q032** How do I patch a small hole in drywall, about the size of a doorknob?
- [ ] **q033** My toilet keeps running after it's flushed. How do I fix it?
- [ ] **q034** How often should I change the air filter in my furnace or HVAC system?
- [ ] **q035** How do I get rid of mildew on the grout in my shower?
- [ ] **q036** How do I stop a door hinge from squeaking?
- [ ] **q037** How do I find a stud in the wall if I don't have a stud finder?
- [ ] **q038** The caulk around my bathtub is cracked and moldy. How do I replace it?
- [ ] **q039** My kitchen faucet drips constantly. How do I fix it?
- [ ] **q040** What's the right order of steps for painting a bedroom?

### 5. Travel and logistics

- [ ] **q041** I'm flying from New York to London overnight next month. What can I do before and after the flight to adjust to the time difference faster?
- [ ] **q042** How do I pack a single carry-on bag for a week-long trip without running out of clothes?
- [ ] **q043** What's a safe amount of time to leave between connecting flights if I have to change terminals?
- [ ] **q044** I need to travel about 400 km between two cities. How should I decide between taking the train and flying?
- [ ] **q045** What's the difference between a plug adapter and a voltage converter, and how do I know which one I need for my hair dryer?
- [ ] **q046** My checked suitcase didn't show up on the carousel. What should I do before leaving the airport?
- [ ] **q047** When I pay by card abroad, the machine sometimes asks if I want to be charged in my home currency. Which option should I pick, and why?
- [ ] **q048** Explain what a typical travel insurance policy covers and what it usually leaves out.
- [ ] **q049** How often should I stop for a break on a 10-hour road trip, and what should I do during the stops?
- [ ] **q050** What are the pros and cons of staying in a hostel instead of a budget hotel?

### 6. Physical science: how things work

- [ ] **q051** Why is the sky blue during the day?
- [ ] **q052** How does a microwave oven actually heat food?
- [ ] **q053** Why does ice float on water when most solids sink in their own liquid?
- [ ] **q054** Explain how a refrigerator moves heat out of its inside to keep food cold.
- [ ] **q055** How do noise-cancelling headphones block out sound?
- [ ] **q056** What keeps a heavy airliner up in the air?
- [ ] **q057** How does my phone's GPS work out where I am?
- [ ] **q058** A metal spoon and a wooden spoon have been sitting in the same drawer, but the metal one feels colder to touch. Why?
- [ ] **q059** How does a rainbow form, and why is it curved?
- [ ] **q060** Why does water boil at a lower temperature at high altitude?

### 7. Biology and nature

- [ ] **q061** Why do leaves turn red and yellow in autumn?
- [ ] **q062** How do bees turn flower nectar into honey?
- [ ] **q063** How do migrating birds find their way over thousands of kilometres?
- [ ] **q064** Explain photosynthesis in simple terms.
- [ ] **q065** Why does cutting an onion make your eyes water?
- [ ] **q066** How does a chameleon change its colour?
- [ ] **q067** What's the difference between a virus and a bacterium?
- [ ] **q068** How do fireflies make their light?
- [ ] **q069** How does water get from the roots all the way to the top of a tall tree?
- [ ] **q070** Why do some animals hibernate, and what happens in their bodies while they do?

### 8. History and culture

- [ ] **q071** Why was the Great Wall of China built?
- [ ] **q072** How did the printing press change everyday life in Europe?
- [ ] **q073** How did the ancient Olympic Games start, and how were they different from the modern Olympics?
- [ ] **q074** Why did the Romans build aqueducts, and how did they get water to flow over such long distances?
- [ ] **q075** What was the Silk Road, and what was traded along it?
- [ ] **q076** Why does a week have seven days?
- [ ] **q077** How do historians think the ancient Egyptians built the pyramids?
- [ ] **q078** What was the Renaissance, and why did it begin in Italy?
- [ ] **q079** Where do Halloween traditions like costumes and carved pumpkins come from?
- [ ] **q080** What's the origin of shaking hands as a greeting?

### 9. Using technology

- [ ] **q081** How do I take a screenshot of just one window on a Windows laptop?
- [ ] **q082** My browser keeps showing an old version of a website I manage. How do I clear the cache in Chrome?
- [ ] **q083** My phone says storage is almost full. What are the quickest ways to free up space without deleting my photos?
- [ ] **q084** What is two-factor authentication, and how do I turn it on for my email account?
- [ ] **q085** I'm connected to Wi-Fi on my Windows PC but forgot the password. Can I see it somewhere so I can connect my phone too?
- [ ] **q086** How do I save a Word document as a PDF?
- [ ] **q087** What are the telltale signs that an email is a phishing attempt?
- [ ] **q088** My laptop froze completely and won't respond to the mouse or keyboard. What should I do?
- [ ] **q089** Explain how to automatically back up the photos on my phone so I don't lose them if the phone breaks.
- [ ] **q090** How do I put two windows side by side on a Mac screen?

### 10. Small coding tasks

- [ ] **q091** Write a Python function that takes a sentence and returns it with the word order reversed, so 'I like tea' becomes 'tea like I'.
- [ ] **q092** This JavaScript is supposed to add up every number in the array, but the result is wrong. What's the bug?
    
    function total(nums) {
      let sum = 0;
      for (let i = 1; i <= nums.length; i++) {
        sum += nums[i];
      }
      return sum;
    }
- [ ] **q093** Write a Python function that checks whether a string is a palindrome, ignoring spaces and capital letters.
- [ ] **q094** I have a SQL table orders(id, customer_id, amount). Write a query that shows how many orders each customer has placed.
- [ ] **q095** Give me a Python regex that pulls all the numbers out of a string like 'Order 12 shipped with 3 items on day 45'.
- [ ] **q096** Why does this Python function keep remembering items from earlier calls, and how do I fix it?
    
    def add_item(item, basket=[]):
        basket.append(item)
        return basket
- [ ] **q097** Write FizzBuzz in Python for the numbers 1 to 100.
- [ ] **q098** What's a bash command to count the total number of lines across all the .py files in a folder?
- [ ] **q099** Write a JavaScript function that converts a temperature from Celsius to Fahrenheit.
- [ ] **q100** My Python script crashes with KeyError: 'email' on this line. How do I make it fall back to a default when the key is missing?
    
    email = user['email']

### 11. Writing help

- [ ] **q101** Can you rewrite this email so it sounds polite but still firm? "Mark, I asked for the quarterly report two weeks ago and still don't have it. I need it by Friday. This is holding everything up."
- [ ] **q102** Write a short email to my landlord saying the heating in my flat stopped working yesterday and asking when it can be repaired.
- [ ] **q103** Help me write a message declining a friend's wedding invitation because I'll be abroad that week.
- [ ] **q104** Shorten this to two sentences: "Our new water bottle is made from stainless steel, so it is very durable. It keeps drinks cold for up to 24 hours and hot for up to 12 hours, so it works in any season. It also has a leak-proof lid, so it won't spill in your bag."
- [ ] **q105** Rewrite this job ad line so it sounds welcoming: "Applicants must have 5+ years experience. No exceptions." *(replaced)*
- [ ] **q106** A customer wrote to us: "I ordered a lamp two weeks ago, it was supposed to arrive in 3 days and it still hasn't come. Very disappointed." Draft a reply from our small online shop.
- [ ] **q107** Write an email to my university lecturer asking for a one-week extension on an essay because I have two other deadlines that same week.
- [ ] **q108** Make this more professional: "hey can u send me the files asap, need them for the meeting thx"
- [ ] **q109** Write a friendly message for my group chat reminding everyone to send me their share for last Saturday's dinner, which came to $32 each.
- [ ] **q110** Rewrite this sentence so it's easier to follow: "The report that was written by the team that was hired by the manager who left last month was reviewed."

### 12. Everyday maths and estimation

- [ ] **q111** Our restaurant bill is $86.40. How much is a 15% tip, and what's the total?
- [ ] **q112** A 500 g box of cereal costs $3.80 and a 750 g box costs $5.40. Which one is better value?
- [ ] **q113** If I drive 340 km at an average of 85 km/h, how long will the trip take?
- [ ] **q114** A jacket is 20% off, and there's an extra 10% off at the till. Is that the same as 30% off?
- [ ] **q115** Roughly how many litres of water does a bathtub hold if it's 1.5 m long, 0.7 m wide and filled 0.4 m deep?
- [ ] **q116** I cycle to work at 20 km/h and back home at 10 km/h along the same road. What's my average speed for the round trip?
- [ ] **q117** How many days are there from 14 March to 2 August in the same year?
- [ ] **q118** Estimate how many times a person's heart beats over an 80-year lifetime.
- [ ] **q119** Three of us share a flat with rent of $2,400 a month. The bedrooms are 15, 12 and 9 square metres. How could we split the rent by room size?
- [ ] **q120** The price of my usual coffee went from $4.00 to $4.60. What percentage increase is that?

### 13. Language, grammar and word usage

- [ ] **q121** What's the difference between 'affect' and 'effect'? I always mix them up.
- [ ] **q122** When should I use a semicolon instead of a comma or a full stop? Please give a couple of examples.
- [ ] **q123** Is it 'fewer calories' or 'less calories'? Explain the rule.
- [ ] **q124** What does the phrase 'bite the bullet' mean, and where does it come from?
- [ ] **q125** How do I know whether to use 'who' or 'whom' in a sentence?
- [ ] **q126** My teacher marked 'to quickly finish' as wrong because it splits the infinitive. Is splitting an infinitive actually an error?
- [ ] **q127** Explain when to use 'i.e.' versus 'e.g.'.
- [ ] **q128** Can you explain what the passive voice is and rewrite this sentence in the active voice: 'The report was written by the committee last week.'
- [ ] **q129** What's the plural of 'cactus'? Is 'cactuses' acceptable?
- [ ] **q130** Lie or lay? I never know which one to use when talking about going to bed or putting something down.

### 14. Studying and learning skills

- [ ] **q131** Can you explain what spaced repetition is and how I'd use it to study for an introductory biology course?
- [ ] **q132** How does the Pomodoro technique work?
- [ ] **q133** Explain the Cornell note-taking method and how to set up a page.
- [ ] **q134** What are good strategies for answering multiple-choice questions when I'm not sure of the answer?
- [ ] **q135** What is the Feynman technique for learning? Walk me through it step by step.
- [ ] **q136** What's interleaved practice, and is it better than doing all the problems of one type at once?
- [ ] **q137** Explain the SQ3R method for reading a textbook.
- [ ] **q138** I have to give a five-minute speech next week without notes. How should I memorise it?
- [ ] **q139** I have four final exams over the next eight days: chemistry, history, calculus and Spanish. Can you suggest how to split my study time?
- [ ] **q140** How does the memory palace technique work? Walk me through an example.

### 15. Fitness and general wellness

- [ ] **q141** I'm new to the gym. Can you give me a simple three-day-a-week full-body routine?
- [ ] **q142** How do I do a proper push-up? What are the common form mistakes?
- [ ] **q143** I've never been a runner. How should I build up to running 5K without stopping?
- [ ] **q144** Roughly how much water should a healthy adult drink in a day?
- [ ] **q145** Give me a five-minute stretching routine I can do at my desk during the workday.
- [ ] **q146** What should a good warm-up before a run include?
- [ ] **q147** What is HIIT, and how is it different from steady cardio?
- [ ] **q148** What are some habits that help you fall asleep faster at night?
- [ ] **q149** Is walking 10,000 steps a day a meaningful goal? How can I fit more steps into my day?
- [ ] **q150** How much protein do people generally aim for when they're trying to build muscle?

### 16. Gardening and pets

- [ ] **q151** How often should I water tomato plants growing in the ground during summer?
- [ ] **q152** How do I start a compost bin in a small backyard?
- [ ] **q153** How do I know when a houseplant needs repotting, and how do I do it?
- [ ] **q154** What's the best way to house-train a new puppy?
- [ ] **q155** We're bringing home a second cat next week. How should we introduce her to our resident cat?
- [ ] **q156** How can I grow basil indoors on a windowsill?
- [ ] **q157** When and how should I prune my rose bushes?
- [ ] **q158** I'm setting up my first freshwater aquarium. What does 'cycling the tank' mean, and how do I do it?
- [ ] **q159** My dog pulls constantly on walks. How do I teach loose-leash walking?
- [ ] **q160** What are some good plants for a garden that gets very little sun?

### 17. Etiquette and everyday communication

- [ ] **q161** What's a polite way to slip out of a conversation at a party when the other person keeps talking and I'd like to mingle?
- [ ] **q162** How much should I tip a food delivery driver, and should it change with distance or bad weather?
- [ ] **q163** I can't make it to a former classmate's wedding. How do I decline the RSVP politely, and should I still send a gift?
- [ ] **q164** Is it rude to wear headphones most of the day in an open-plan office?
- [ ] **q165** Explain the proper way to introduce two people to each other, including whose name you say first.
- [ ] **q166** Write a short thank-you note for a gift I don't actually like, without lying outright.
- [ ] **q167** My neighbour's car often half-blocks my driveway. How do I bring it up without starting a feud?
- [ ] **q168** Is it acceptable to take a phone call on speaker on a train or bus?
- [ ] **q169** How long should I wait before following up on an email to an acquaintance who hasn't replied?
- [ ] **q170** People constantly mispronounce my surname. How can I correct them without making it awkward?

### 18. Planning and organising

- [ ] **q171** Make a fair weekly chore rota for four adults sharing a flat with a kitchen, two bathrooms and a living room.
- [ ] **q172** How should I organise a small reach-in closet that's overflowing?
- [ ] **q173** I'm hosting a birthday picnic for ten people in a park next Saturday. Give me a timeline for the week before and for the day itself.
- [ ] **q174** Explain the Eisenhower matrix and how to use it on a messy to-do list.
- [ ] **q175** In what order should I pack up the rooms of a two-bedroom flat when moving?
- [ ] **q176** Help me design a weekday morning routine so that my two kids and I are out of the house by 7:30.
- [ ] **q177** What's a sensible folder structure for organising ten years of digital photos?
- [ ] **q178** How do I plan and run a successful garage sale?
- [ ] **q179** Our family keeps double-booking evenings and weekends. How should we set up a shared calendar system that actually works?
- [ ] **q180** What's the best way to tackle a cluttered junk drawer?

### 19. Buying and comparing things

- [ ] **q181** How do I choose the right mattress firmness for me?
- [ ] **q182** What should I check before buying a used bicycle from a stranger?
- [ ] **q183** Bagged or bagless vacuum cleaner: which should I buy, and why?
- [ ] **q184** Down or synthetic insulation for a winter coat? What are the trade-offs?
- [ ] **q185** Is an extended warranty on a new appliance usually worth paying for?
- [ ] **q186** What size TV should I get if my sofa is about three metres from the wall?
- [ ] **q187** What should I look for when buying my first good chef's knife?
- [ ] **q188** Give me a list of questions to ask a private seller before buying their used car.
- [ ] **q189** Which laptop specs actually matter for a university student who mostly writes essays and streams videos?
- [ ] **q190** Should I buy a refurbished phone or a new one? What are the risks of refurbished?

### 20. Hobbies and creative pursuits

- [ ] **q191** I want to learn to knit. What should my very first project be, and what supplies do I need?
- [ ] **q192** What are the basic principles of a good chess opening?
- [ ] **q193** Explain the rules of a haiku and write one about autumn rain.
- [ ] **q194** What is the rule of thirds in photography, and when should I break it?
- [ ] **q195** Explain the difference between wet-on-wet and wet-on-dry watercolour techniques.
- [ ] **q196** How do I tune a guitar by ear without a tuner?
- [ ] **q197** How do I get started with birdwatching?
- [ ] **q198** Give me step-by-step instructions for folding an origami crane.
- [ ] **q199** I'm running my first tabletop role-playing session as game master for four friends next week. None of us have played before. How should I prepare?
- [ ] **q200** What's the most efficient way to approach a 1000-piece jigsaw puzzle?

## Training prompts: random sample (5 per category, seed 7; full list in `train_pool_draft.jsonl`)

-  1 **t0042** My beef stew is too thin. How can I thicken it?
-  1 **t0020** Can I swap dark brown sugar for light brown sugar in a recipe? What changes?
-  1 **t0051** What's the difference between all-purpose flour and bread flour?
-  1 **t0084** Walk me through cooking fresh mussels.
-  1 **t0007** What's the difference between braising and stewing?
-  2 **t0110** Why is paying only the minimum on a credit card balance so expensive?
-  2 **t0169** How do I do a no-spend month?
-  2 **t0113** How do I negotiate a lower monthly price with my internet provider?
-  2 **t0147** Help me turn 'save more money' into a specific, measurable goal.
-  2 **t0175** What does it mean to refinance a loan?
-  3 **t0208** Explain how to structure a cover letter.
-  3 **t0265** What should a project kickoff document include?
-  3 **t0228** I'm a new team lead. How do I delegate tasks well?
-  3 **t0205** How should I set up my room, lighting, and camera for a video interview?
-  3 **t0212** Give me tips for networking at a professional conference when I don't know anyone there.
-  4 **t0356** An old painted window sash is stuck shut. How can I get it open?
-  4 **t0354** My garbage disposal hums but doesn't spin. How do I fix it?
-  4 **t0309** How do I winterize outdoor faucets before the first freeze?
-  4 **t0331** How can I repair light scratches in a hardwood floor?
-  4 **t0312** How do I fix a wobbly kitchen chair?
-  5 **t0471** How should I pack for a destination where the weather can change quickly from day to day?
-  5 **t0455** Should I take a regular taxi or a ride-hailing app from the airport? What are the trade-offs?
-  5 **t0408** Can you explain how frequent flyer programs let you earn and spend points, in plain terms?
-  5 **t0473** What should I pack for my first ski trip?
-  5 **t0416** How early should I get to the airport for an international flight?
-  6 **t0529** Explain the Doppler effect using the example of an ambulance driving past.
-  6 **t0581** How does a rocket speed up in space when there's no air to push against?
-  6 **t0575** Why does a kettle get loud just before the water starts boiling, then go quieter?
-  6 **t0508** How does an electric motor turn electricity into motion?
-  6 **t0574** Why do bridges have gaps in them called expansion joints?
-  7 **t0675** Why do pine cones open in dry weather and close when it's damp?
-  7 **t0651** How does our sense of smell actually work?
-  7 **t0607** Explain how giraffes ended up with such long necks, from an evolutionary point of view.
-  7 **t0629** How can a gecko walk up a glass window?
-  7 **t0606** How can whales hold their breath for so long?
-  8 **t0772** Describe Magellan's expedition and how the first trip around the world was completed.
-  8 **t0718** Why was the Terracotta Army buried with China's first emperor?
-  8 **t0738** Why did the Titanic sink, and why did so many people die?
-  8 **t0754** Where does the necktie come from?
-  8 **t0719** Who carved the city of Petra into the rock, and how did it get rich?
-  9 **t0870** How do I connect a second monitor to my laptop and set it to extend the desktop rather than mirror it?
-  9 **t0816** My grandmother finds the text on her phone too small to read. How can I make it bigger?
-  9 **t0874** Is it bad for my phone battery to charge it overnight?
-  9 **t0840** My computer has become sluggish. How do I use Task Manager to see what's eating up resources?
-  9 **t0872** What's the difference between sleep, hibernate and shut down on a laptop?
- 10 **t0988** How do I throw away my uncommitted changes to just one file in git?
- 10 **t0924** Format the current time in Python as hours and minutes, like 14:05.
- 10 **t0914** Use a list comprehension to get the squares of all the even numbers from 1 to 20.
- 10 **t0975** In Python 3, 7 / 2 gives 3.5. How do I get whole-number division, and what happens with negative numbers?
- 10 **t0974** Inside this object method, `this.count` is undefined in the callback. How do I fix it?
- 11 **t1082** Draft a message to a group of friends proposing a hiking trip on the 14th and asking who's in.
- 11 **t1025** Draft a complaint email to my internet provider about the connection dropping every evening for the past week.
- 11 **t1048** Write a short paragraph for a flyer advertising a community garage sale at the church hall, Saturday 9am to 1pm.
- 11 **t1013** Make this sound more confident: "I think maybe I could possibly help with the event planning, if that's okay?"
- 11 **t1071** Rewrite this feedback so it's constructive: "The report is confusing and has too many typos."
- 12 **t1192** What's the chance of drawing a heart from a standard deck, and then another heart if I don't put the first card back?
- 12 **t1109** Sales tax is 8.25%. What's the total for a $64 purchase?
- 12 **t1173** How long will a 4.2 GB file take to download at 50 megabits per second?
- 12 **t1108** Overtime is paid at time and a half. My normal rate is $18 an hour. How much do I earn for 6 hours of overtime?
- 12 **t1180** A candle burns down 1.5 cm per hour and is 18 cm tall. How long will it last?
- 13 **t1227** Is it 'piqued my interest', 'peaked my interest' or 'peeked my interest'?
- 13 **t1264** What does 'spill the beans' mean? Give me two example sentences.
- 13 **t1288** Should it be 'Each of the students has' or 'Each of the students have'?
- 13 **t1269** What is the origin of the word 'goodbye'?
- 13 **t1255** My first language doesn't have articles. How do English speakers decide between 'a', 'the' and nothing at all?
- 14 **t1400** How can I set up accountability so I keep studying when no one is checking on me?
- 14 **t1341** How do I take useful notes from video lectures online?
- 14 **t1360** What is elaborative interrogation, and how do I use it?
- 14 **t1375** How do I write the discussion section of a school lab report?
- 14 **t1359** What is dual coding in learning? Give an example for studying the water cycle.
- 15 **t1447** What is mindful eating, and how do I practise it?
- 15 **t1439** How long should a typical gym session be?
- 15 **t1432** What core exercises are better than crunches?
- 15 **t1424** What is a tempo run?
- 15 **t1490** Any tips for my first time bouldering at a climbing gym?
- 16 **t1600** How often should a 10-week-old kitten be fed?
- 16 **t1532** How do I keep a rosemary plant alive through winter?
- 16 **t1511** What is companion planting? Give a few classic pairings.
- 16 **t1574** How do I trim my cat's claws?
- 16 **t1539** How do I plant and care for rhubarb?
- 17 **t1668** What small talk topics should I avoid with people I've just met?
- 17 **t1664** How late can I arrive to a dinner party before it becomes rude?
- 17 **t1644** What etiquette should I follow when visiting a Buddhist temple in Thailand?
- 17 **t1694** How do I get a server's attention in a busy restaurant without waving or snapping my fingers?
- 17 **t1658** Our houseguests haven't said when they're leaving. How do I ask about their plans tactfully?
- 18 **t1737** I want to host a board game night for eight people, some of whom don't know each other and some who've never played anything beyond the classics. How should I o
- 18 **t1778** Write a checklist for a house-sitter covering a two-week absence.
- 18 **t1710** What is a weekly review, and what steps should it include?
- 18 **t1716** Our extended family wants a reunion next summer for about 40 people. Where do I start?
- 18 **t1766** What would a 15-minute daily tidy routine look like?
- 19 **t1854** Acoustic piano or digital piano for an adult beginner?
- 19 **t1822** Tower fan, pedestal fan or box fan for a hot bedroom?
- 19 **t1897** What does the joule rating on a surge protector mean?
- 19 **t1844** Hiking boots or trail running shoes for day hikes?
- 19 **t1820** What is CADR on an air purifier, and how do I use it to choose one for a bedroom?
- 20 **t1963** How do I bind a simple booklet with a pamphlet stitch?
- 20 **t1954** Which fishing knot should a beginner learn first, and how do I tie it?
- 20 **t1906** How do you centre clay on a pottery wheel?
- 20 **t1986** How do I draw a fantasy map for a world I'm writing?
- 20 **t1910** Explain how one-point perspective works in drawing.

## Items replaced to clear the checks

| id | category | new text |
|---|---|---|
| q105 | 11 | Rewrite this job ad line so it sounds welcoming: "Applicants must have 5+ years experience. No exceptions." |
| t0040 | 1 | How can I tell when a steak is done without cutting into it? |
| t0131 | 2 | How do I work out how much of my take-home pay goes on subscriptions each month, and which to cut first? |
| t0191 | 2 | What happens if I accidentally overpay my credit card bill? |
| t0219 | 3 | How do I ask my manager for more regular feedback without it sounding needy? |
| t0929 | 10 | Write a Python function that returns the second-largest number in a list, handling duplicates. |
| t1087 | 11 | Turn these notes into a short paragraph for a staff newsletter: office closed Monday for heating repairs; reopening Tuesday 9am; urgent issues to the front desk number. |
| t1091 | 11 | Shorten this without losing meaning: "Due to the fact that the meeting has been moved, we will need to reschedule the presentation at a later point in time." |
| t1636 | 17 | What's the polite way to suggest sharing a taxi with a stranger at the airport? |
| t1711 | 18 | Help me plan a three-day weekend visit from my parents, with one rainy-day option. |
| t1747 | 18 | What's a simple system for keeping track of birthdays and sending cards on time? |
| t1779 | 18 | Plan a week of activities for an eight-year-old niece who's visiting during school holidays. |
| t1827 | 19 | What should I consider when choosing a bike lock? |
