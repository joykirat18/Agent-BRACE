Use MAX_STATIC_DATA of 500000.
When play begins, seed the random-number generator with 1234.

container is a kind of thing.
door is a kind of thing.
object-like is a kind of thing.
supporter is a kind of thing.
food is a kind of object-like.
key is a kind of object-like.
containers are openable, lockable and fixed in place. containers are usually closed.
door is openable and lockable.
object-like is portable.
supporters are fixed in place.
food is edible.
A room has a text called internal name.


The r_0 and the r_8 and the r_1 and the r_12 and the r_10 and the r_13 and the r_11 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_7 and the r_19 and the r_9 are rooms.

Understand "chamber" as r_0.
The internal name of r_0 is "chamber".
The printed name of r_0 is "-= Chamber =-".
The chamber part 0 is some text that varies. The chamber part 0 is "Well, here we are in the chamber.

 You can see a dresser.[if c_0 is open and there is something in the c_0] The dresser contains [a list of things in the c_0]. Now that's what I call TextWorld![end if]".
The chamber part 1 is some text that varies. The chamber part 1 is "[if c_0 is open and the c_0 contains nothing] The dresser is empty! What a waste of a day![end if]".
The chamber part 2 is some text that varies. The chamber part 2 is "

 There is [if d_3 is open]an open[otherwise]a closed[end if]".
The chamber part 3 is some text that varies. The chamber part 3 is " hatch leading west. You don't like doors? Why not try going east, that entranceway is unguarded. You need an unguarded exit? You should try going north.".
The description of r_0 is "[chamber part 0][chamber part 1][chamber part 2][chamber part 3]".

west of r_0 and east of r_8 is a door called d_3.
The r_7 is mapped north of r_0.
The r_1 is mapped east of r_0.
Understand "kitchenette" as r_8.
The internal name of r_8 is "kitchenette".
The printed name of r_8 is "-= Kitchenette =-".
The kitchenette part 0 is some text that varies. The kitchenette part 0 is "Okay, so you're in a kitchenette, cool, but is it normal? You better believe it is.

 You make out [if c_1 is locked]a locked[else if c_1 is open]an opened[otherwise]a closed[end if]".
The kitchenette part 1 is some text that varies. The kitchenette part 1 is " fridge.[if c_1 is open and there is something in the c_1] The fridge contains [a list of things in the c_1]. Huh, weird.[end if]".
The kitchenette part 2 is some text that varies. The kitchenette part 2 is "[if c_1 is open and the c_1 contains nothing] The fridge is empty, what a horrible day![end if]".
The kitchenette part 3 is some text that varies. The kitchenette part 3 is " You can see a saucepan. [if there is something on the s_0]On the saucepan you can see [a list of things on the s_0]. Suddenly, you bump your head on the ceiling, but it's not such a bad bump that it's going to prevent you from looking at objects and even things.[end if]".
The kitchenette part 4 is some text that varies. The kitchenette part 4 is "[if there is nothing on the s_0]But the thing is empty.[end if]".
The kitchenette part 5 is some text that varies. The kitchenette part 5 is " You make out a rack. You shudder, but continue examining the rack. The rack is ordinary.[if there is something on the s_1] On the rack you make out [a list of things on the s_1]. Now that's what I call TextWorld![end if]".
The kitchenette part 6 is some text that varies. The kitchenette part 6 is "[if there is nothing on the s_1] But oh no! there's nothing on this piece of junk.[end if]".
The kitchenette part 7 is some text that varies. The kitchenette part 7 is "

 There is [if d_3 is open]an open[otherwise]a closed[end if]".
The kitchenette part 8 is some text that varies. The kitchenette part 8 is " hatch leading east. There is [if d_2 is open]an open[otherwise]a closed[end if]".
The kitchenette part 9 is some text that varies. The kitchenette part 9 is " portal leading south.".
The description of r_8 is "[kitchenette part 0][kitchenette part 1][kitchenette part 2][kitchenette part 3][kitchenette part 4][kitchenette part 5][kitchenette part 6][kitchenette part 7][kitchenette part 8][kitchenette part 9]".

south of r_8 and north of r_9 is a door called d_2.
east of r_8 and west of r_0 is a door called d_3.
Understand "shower" as r_1.
The internal name of r_1 is "shower".
The printed name of r_1 is "-= Shower =-".
The shower part 0 is some text that varies. The shower part 0 is "You find yourself in a shower. An ordinary one.



There is an unguarded exit to the east. You need an unblocked exit? You should try going west.".
The description of r_1 is "[shower part 0]".

The r_0 is mapped west of r_1.
The r_2 is mapped east of r_1.
Understand "bedchamber" as r_12.
The internal name of r_12 is "bedchamber".
The printed name of r_12 is "-= Bedchamber =-".
The bedchamber part 0 is some text that varies. The bedchamber part 0 is "You are in a bedchamber. A standard kind of place. The room is well lit.

 You make out [if c_2 is locked]a locked[else if c_2 is open]an opened[otherwise]a closed[end if]".
The bedchamber part 1 is some text that varies. The bedchamber part 1 is " basket close by.[if c_2 is open and there is something in the c_2] The basket contains [a list of things in the c_2].[end if]".
The bedchamber part 2 is some text that varies. The bedchamber part 2 is "[if c_2 is open and the c_2 contains nothing] The basket is empty, what a horrible day![end if]".
The bedchamber part 3 is some text that varies. The bedchamber part 3 is "

There is an exit to the east. Don't worry, it is unblocked. You don't like doors? Why not try going south, that entranceway is unblocked. You need an unblocked exit? You should try going west.".
The description of r_12 is "[bedchamber part 0][bedchamber part 1][bedchamber part 2][bedchamber part 3]".

The r_10 is mapped west of r_12.
The r_13 is mapped south of r_12.
The r_15 is mapped east of r_12.
Understand "workshop" as r_10.
The internal name of r_10 is "workshop".
The printed name of r_10 is "-= Workshop =-".
The workshop part 0 is some text that varies. The workshop part 0 is "You've entered a workshop.

 You can see a case.[if c_3 is open and there is something in the c_3] The case contains [a list of things in the c_3].[end if]".
The workshop part 1 is some text that varies. The workshop part 1 is "[if c_3 is open and the c_3 contains nothing] What a letdown! The case is empty![end if]".
The workshop part 2 is some text that varies. The workshop part 2 is " As if things weren't amazing enough already, you can even see a mantle. What a coincidence, weren't you just thinking about a mantle? The mantle is typical.[if there is something on the s_2] On the mantle you can see [a list of things on the s_2].[end if]".
The workshop part 3 is some text that varies. The workshop part 3 is "[if there is nothing on the s_2] But oh no! there's nothing on this piece of junk.[end if]".
The workshop part 4 is some text that varies. The workshop part 4 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The workshop part 5 is some text that varies. The workshop part 5 is " gate leading north. You don't like doors? Why not try going east, that entranceway is unguarded. You don't like doors? Why not try going south, that entranceway is unguarded.".
The description of r_10 is "[workshop part 0][workshop part 1][workshop part 2][workshop part 3][workshop part 4][workshop part 5]".

The r_11 is mapped south of r_10.
north of r_10 and south of r_9 is a door called d_1.
The r_12 is mapped east of r_10.
Understand "recreation zone" as r_13.
The internal name of r_13 is "recreation zone".
The printed name of r_13 is "-= Recreation Zone =-".
The recreation zone part 0 is some text that varies. The recreation zone part 0 is "I just think it's great that you've just entered a recreation zone. You try to gain information on your surroundings by using a technique you call 'looking.'



You don't like doors? Why not try going east, that entranceway is unblocked. You need an unblocked exit? You should try going north. You need an unblocked exit? You should try going west.".
The description of r_13 is "[recreation zone part 0]".

The r_11 is mapped west of r_13.
The r_12 is mapped north of r_13.
The r_14 is mapped east of r_13.
Understand "bedroom" as r_11.
The internal name of r_11 is "bedroom".
The printed name of r_11 is "-= Bedroom =-".
The bedroom part 0 is some text that varies. The bedroom part 0 is "You find yourself in a bedroom. A standard one. You decide to just list off a complete list of everything you see in the room, because hey, why not?



There is an unblocked exit to the east. You don't like doors? Why not try going north, that entranceway is unblocked.".
The description of r_11 is "[bedroom part 0]".

The r_10 is mapped north of r_11.
The r_13 is mapped east of r_11.
Understand "office" as r_14.
The internal name of r_14 is "office".
The printed name of r_14 is "-= Office =-".
The office part 0 is some text that varies. The office part 0 is "You've just shown up in an office. You begin to take stock of what's here.



You need an unblocked exit? You should try going east. There is an exit to the north. Don't worry, it is unblocked. There is an unguarded exit to the west.".
The description of r_14 is "[office part 0]".

The r_13 is mapped west of r_14.
The r_15 is mapped north of r_14.
The r_16 is mapped east of r_14.
Understand "basement" as r_15.
The internal name of r_15 is "basement".
The printed name of r_15 is "-= Basement =-".
The basement part 0 is some text that varies. The basement part 0 is "You are in a basement. It seems to be pretty standard here.

 If you haven't noticed it already, there seems to be something there by the wall, it's a table. The table is typical.[if there is something on the s_3] On the table you make out [a list of things on the s_3].[end if]".
The basement part 1 is some text that varies. The basement part 1 is "[if there is nothing on the s_3] Unfortunately, there isn't a thing on it.[end if]".
The basement part 2 is some text that varies. The basement part 2 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The basement part 3 is some text that varies. The basement part 3 is " door leading east. There is an unblocked exit to the north. There is an exit to the south. Don't worry, it is unguarded. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_15 is "[basement part 0][basement part 1][basement part 2][basement part 3]".

The r_12 is mapped west of r_15.
The r_14 is mapped south of r_15.
The r_19 is mapped north of r_15.
east of r_15 and west of r_17 is a door called d_0.
Understand "playroom" as r_16.
The internal name of r_16 is "playroom".
The printed name of r_16 is "-= Playroom =-".
The playroom part 0 is some text that varies. The playroom part 0 is "You are in a playroom. A standard one.

 You make out [if c_4 is locked]a locked[else if c_4 is open]an opened[otherwise]a closed[end if]".
The playroom part 1 is some text that varies. The playroom part 1 is " coffer.[if c_4 is open and there is something in the c_4] The coffer contains [a list of things in the c_4].[end if]".
The playroom part 2 is some text that varies. The playroom part 2 is "[if c_4 is open and the c_4 contains nothing] The coffer is empty! What a waste of a day![end if]".
The playroom part 3 is some text that varies. The playroom part 3 is "

There is an unguarded exit to the north. You need an unguarded exit? You should try going west.".
The description of r_16 is "[playroom part 0][playroom part 1][playroom part 2][playroom part 3]".

The r_14 is mapped west of r_16.
The r_17 is mapped north of r_16.
Understand "salon" as r_17.
The internal name of r_17 is "salon".
The printed name of r_17 is "-= Salon =-".
The salon part 0 is some text that varies. The salon part 0 is "You arrive in a salon. A normal kind of place. You begin looking for stuff.



 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The salon part 1 is some text that varies. The salon part 1 is " door leading west. There is an unguarded exit to the east. You don't like doors? Why not try going south, that entranceway is unblocked.".
The description of r_17 is "[salon part 0][salon part 1]".

west of r_17 and east of r_15 is a door called d_0.
The r_16 is mapped south of r_17.
The r_18 is mapped east of r_17.
Understand "study" as r_18.
The internal name of r_18 is "study".
The printed name of r_18 is "-= Study =-".
The study part 0 is some text that varies. The study part 0 is "You find yourself in a study. A normal kind of place.



You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_18 is "[study part 0]".

The r_17 is mapped west of r_18.
Understand "parlor" as r_2.
The internal name of r_2 is "parlor".
The printed name of r_2 is "-= Parlor =-".
The parlor part 0 is some text that varies. The parlor part 0 is "You find yourself in a parlor. A normal kind of place. You begin to take stock of what's in the room.

 You see a gleam over in a corner, where you can see a bench. [if there is something on the s_4]You see [a list of things on the s_4] on the bench. Hmmm... what else, what else?[end if]".
The parlor part 1 is some text that varies. The parlor part 1 is "[if there is nothing on the s_4]But oh no! there's nothing on this piece of junk.[end if]".
The parlor part 2 is some text that varies. The parlor part 2 is "

You need an unguarded exit? You should try going east. You don't like doors? Why not try going west, that entranceway is unblocked.".
The description of r_2 is "[parlor part 0][parlor part 1][parlor part 2]".

The r_1 is mapped west of r_2.
The r_3 is mapped east of r_2.
Understand "spare room" as r_3.
The internal name of r_3 is "spare room".
The printed name of r_3 is "-= Spare Room =-".
The spare room part 0 is some text that varies. The spare room part 0 is "You find yourself in a spare room. An ordinary kind of place. Let's see what's in here.

 You make out a crate.[if c_5 is open and there is something in the c_5] The crate contains [a list of things in the c_5].[end if]".
The spare room part 1 is some text that varies. The spare room part 1 is "[if c_5 is open and the c_5 contains nothing] What a letdown! The crate is empty![end if]".
The spare room part 2 is some text that varies. The spare room part 2 is " You can make out a workbench. The workbench is standard.[if there is something on the s_5] On the workbench you make out [a list of things on the s_5]. Now that's what I call TextWorld![end if]".
The spare room part 3 is some text that varies. The spare room part 3 is "[if there is nothing on the s_5] Looks like someone's already been here and taken everything off it, though. What, you think everything in TextWorld should have stuff on it?[end if]".
The spare room part 4 is some text that varies. The spare room part 4 is " You see a stand. [if there is something on the s_6]You see [a list of things on the s_6] on the stand.[end if]".
The spare room part 5 is some text that varies. The spare room part 5 is "[if there is nothing on the s_6]But the thing is empty.[end if]".
The spare room part 6 is some text that varies. The spare room part 6 is "

You don't like doors? Why not try going north, that entranceway is unguarded. There is an unguarded exit to the west.".
The description of r_3 is "[spare room part 0][spare room part 1][spare room part 2][spare room part 3][spare room part 4][spare room part 5][spare room part 6]".

The r_2 is mapped west of r_3.
The r_4 is mapped north of r_3.
Understand "cubicle" as r_4.
The internal name of r_4 is "cubicle".
The printed name of r_4 is "-= Cubicle =-".
The cubicle part 0 is some text that varies. The cubicle part 0 is "You are in a cubicle. It seems to be pretty standard here. Okay, just remember what you're here to do, and everything will go great.

 If you haven't noticed it already, there seems to be something there by the wall, it's a mantelpiece. You shudder, but continue examining the mantelpiece. The mantelpiece is usual.[if there is something on the s_7] On the mantelpiece you see [a list of things on the s_7].[end if]".
The cubicle part 1 is some text that varies. The cubicle part 1 is "[if there is nothing on the s_7] The mantelpiece appears to be empty. You move on, clearly furious with your TextWorld experience.[end if]".
The cubicle part 2 is some text that varies. The cubicle part 2 is " Look over there! a bookshelf. The bookshelf is typical.[if there is something on the s_8] On the bookshelf you make out [a list of things on the s_8].[end if]".
The cubicle part 3 is some text that varies. The cubicle part 3 is "[if there is nothing on the s_8] But the thing is empty, unfortunately.[end if]".
The cubicle part 4 is some text that varies. The cubicle part 4 is "

You need an unguarded exit? You should try going south. You don't like doors? Why not try going west, that entranceway is unblocked.".
The description of r_4 is "[cubicle part 0][cubicle part 1][cubicle part 2][cubicle part 3][cubicle part 4]".

The r_5 is mapped west of r_4.
The r_3 is mapped south of r_4.
Understand "studio" as r_5.
The internal name of r_5 is "studio".
The printed name of r_5 is "-= Studio =-".
The studio part 0 is some text that varies. The studio part 0 is "You are in a studio. A standard kind of place.



You don't like doors? Why not try going east, that entranceway is unblocked. You need an unguarded exit? You should try going west.".
The description of r_5 is "[studio part 0]".

The r_6 is mapped west of r_5.
The r_4 is mapped east of r_5.
Understand "launderette" as r_6.
The internal name of r_6 is "launderette".
The printed name of r_6 is "-= Launderette =-".
The launderette part 0 is some text that varies. The launderette part 0 is "If you're wondering why everything seems so normal all of a sudden, it's because you've just sauntered into the launderette.

 You make out a cabinet. You idly wonder how they came up with the name TextWorld for this place. It's pretty fitting.[if c_6 is open and there is something in the c_6] The cabinet contains [a list of things in the c_6]. Hmmm... what else, what else?[end if]".
The launderette part 1 is some text that varies. The launderette part 1 is "[if c_6 is open and the c_6 contains nothing] The cabinet is empty! What a waste of a day![end if]".
The launderette part 2 is some text that varies. The launderette part 2 is " You can make out a shelf. The shelf is standard.[if there is something on the s_10] On the shelf you make out [a list of things on the s_10].[end if]".
The launderette part 3 is some text that varies. The launderette part 3 is "[if there is nothing on the s_10] But there isn't a thing on it. Oh! Why couldn't there just be stuff on it?[end if]".
The launderette part 4 is some text that varies. The launderette part 4 is " You can make out a counter. The counter is ordinary.[if there is something on the s_9] On the counter you can make out [a list of things on the s_9].[end if]".
The launderette part 5 is some text that varies. The launderette part 5 is "[if there is nothing on the s_9] Unfortunately, there isn't a thing on it.[end if]".
The launderette part 6 is some text that varies. The launderette part 6 is "

You don't like doors? Why not try going east, that entranceway is unguarded. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_6 is "[launderette part 0][launderette part 1][launderette part 2][launderette part 3][launderette part 4][launderette part 5][launderette part 6]".

The r_7 is mapped west of r_6.
The r_5 is mapped east of r_6.
Understand "austere cubicle" as r_7.
The internal name of r_7 is "austere cubicle".
The printed name of r_7 is "-= Austere Cubicle =-".
The austere cubicle part 0 is some text that varies. The austere cubicle part 0 is "You are in a cubicle. It seems to be pretty austere here.



There is an exit to the east. Don't worry, it is unblocked. You need an unblocked exit? You should try going south.".
The description of r_7 is "[austere cubicle part 0]".

The r_0 is mapped south of r_7.
The r_6 is mapped east of r_7.
Understand "restroom" as r_19.
The internal name of r_19 is "restroom".
The printed name of r_19 is "-= Restroom =-".
The restroom part 0 is some text that varies. The restroom part 0 is "You arrive in a restroom. An ordinary kind of place. Let's see what's in here.



There is an exit to the south. Don't worry, it is unguarded.".
The description of r_19 is "[restroom part 0]".

The r_15 is mapped south of r_19.
Understand "bathroom" as r_9.
The internal name of r_9 is "bathroom".
The printed name of r_9 is "-= Bathroom =-".
The bathroom part 0 is some text that varies. The bathroom part 0 is "You've just sauntered into a bathroom. You begin to take stock of what's in the room.

 You see a trunk.[if c_7 is open and there is something in the c_7] The trunk contains [a list of things in the c_7]. You can't wait to tell the folks at home about this![end if]".
The bathroom part 1 is some text that varies. The bathroom part 1 is "[if c_7 is open and the c_7 contains nothing] What a letdown! The trunk is empty![end if]".
The bathroom part 2 is some text that varies. The bathroom part 2 is " You can see a board. The board is usual.[if there is something on the s_11] On the board you see [a list of things on the s_11]. I mean, just wow! Isn't TextWorld just the best?[end if]".
The bathroom part 3 is some text that varies. The bathroom part 3 is "[if there is nothing on the s_11] Looks like someone's already been here and taken everything off it, though.[end if]".
The bathroom part 4 is some text that varies. The bathroom part 4 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The bathroom part 5 is some text that varies. The bathroom part 5 is " portal leading north. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The bathroom part 6 is some text that varies. The bathroom part 6 is " gate leading south.".
The description of r_9 is "[bathroom part 0][bathroom part 1][bathroom part 2][bathroom part 3][bathroom part 4][bathroom part 5][bathroom part 6]".

south of r_9 and north of r_10 is a door called d_1.
north of r_9 and south of r_8 is a door called d_2.

The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 are containers.
The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 are privately-named.
The d_3 and the d_1 and the d_0 and the d_2 are doors.
The d_3 and the d_1 and the d_0 and the d_2 are privately-named.
The k_1 and the k_0 are keys.
The k_1 and the k_0 are privately-named.
The r_0 and the r_8 and the r_1 and the r_12 and the r_10 and the r_13 and the r_11 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_7 and the r_19 and the r_9 are rooms.
The r_0 and the r_8 and the r_1 and the r_12 and the r_10 and the r_13 and the r_11 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_7 and the r_19 and the r_9 are privately-named.
The s_0 and the s_1 and the s_10 and the s_11 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are supporters.
The s_0 and the s_1 and the s_10 and the s_11 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are privately-named.

The description of d_3 is "it is what it is, a hatch [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_3 is "hatch".
Understand "hatch" as d_3.
The d_3 is open.
The description of d_1 is "The gate looks well-built. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_1 is "gate".
Understand "gate" as d_1.
The d_1 is open.
The description of d_0 is "The door looks well-built. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_0 is "door".
Understand "door" as d_0.
The d_0 is open.
The description of d_2 is "The portal looks robust. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_2 is "portal".
Understand "portal" as d_2.
The d_2 is open.
The description of c_0 is "The dresser looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_0 is "dresser".
Understand "dresser" as c_0.
The c_0 is in r_0.
The c_0 is closed.
The description of c_1 is "The fridge looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_1 is "fridge".
Understand "fridge" as c_1.
The c_1 is in r_8.
The c_1 is locked.
The description of c_2 is "The basket looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_2 is "basket".
Understand "basket" as c_2.
The c_2 is in r_12.
The c_2 is open.
The description of c_3 is "The case looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "case".
Understand "case" as c_3.
The c_3 is in r_10.
The c_3 is closed.
The description of c_4 is "The coffer looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_4 is "coffer".
Understand "coffer" as c_4.
The c_4 is in r_16.
The c_4 is closed.
The description of c_5 is "The crate looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_5 is "crate".
Understand "crate" as c_5.
The c_5 is in r_3.
The c_5 is open.
The description of c_6 is "The cabinet looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_6 is "cabinet".
Understand "cabinet" as c_6.
The c_6 is in r_6.
The c_6 is open.
The description of c_7 is "The trunk looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_7 is "trunk".
Understand "trunk" as c_7.
The c_7 is in r_9.
The c_7 is closed.
The description of k_1 is "The passkey looks useful".
The printed name of k_1 is "passkey".
Understand "passkey" as k_1.
The k_1 is in r_19.
The description of s_0 is "The saucepan is wobbly.".
The printed name of s_0 is "saucepan".
Understand "saucepan" as s_0.
The s_0 is in r_8.
The description of s_1 is "The rack is solid.".
The printed name of s_1 is "rack".
Understand "rack" as s_1.
The s_1 is in r_8.
The description of s_10 is "The shelf is wobbly.".
The printed name of s_10 is "shelf".
Understand "shelf" as s_10.
The s_10 is in r_6.
The description of s_11 is "The board is balanced.".
The printed name of s_11 is "board".
Understand "board" as s_11.
The s_11 is in r_9.
The description of s_2 is "The mantle is undependable.".
The printed name of s_2 is "mantle".
Understand "mantle" as s_2.
The s_2 is in r_10.
The description of s_3 is "The table is shaky.".
The printed name of s_3 is "table".
Understand "table" as s_3.
The s_3 is in r_15.
The description of s_4 is "The bench is unstable.".
The printed name of s_4 is "bench".
Understand "bench" as s_4.
The s_4 is in r_2.
The description of s_5 is "The workbench is stable.".
The printed name of s_5 is "workbench".
Understand "workbench" as s_5.
The s_5 is in r_3.
The description of s_6 is "The stand is an unstable piece of garbage.".
The printed name of s_6 is "stand".
Understand "stand" as s_6.
The s_6 is in r_3.
The description of s_7 is "The mantelpiece is wobbly.".
The printed name of s_7 is "mantelpiece".
Understand "mantelpiece" as s_7.
The s_7 is in r_4.
The description of s_8 is "The bookshelf is solid.".
The printed name of s_8 is "bookshelf".
Understand "bookshelf" as s_8.
The s_8 is in r_4.
The description of s_9 is "The counter is durable.".
The printed name of s_9 is "counter".
Understand "counter" as s_9.
The s_9 is in r_6.
The description of k_0 is "The keycard is cold to the touch".
The printed name of k_0 is "keycard".
Understand "keycard" as k_0.
The k_0 is on the s_0.


The player is in r_16.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.

Test quest0_0 with "go west / go west / go north / go west / go north / go north / take keycard from saucepan"

Every turn:
	if quest0 completed is true:
		do nothing;
	else if The player carries the k_1:
		end the story; [Lost]
	else if The player is in r_8 and The s_0 is in r_8 and The player carries the k_0:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest0 completed is true;

Use scoring. The maximum score is 1.
This is the simpler notify score changes rule:
	If the score is not the last notified score:
		let V be the score - the last notified score;
		if V > 0:
			say "Your score has just gone up by [V in words] ";
		else:
			say "Your score changed by [V in words] ";
		if V >= -1 and V <= 1:
			say "point.";
		else:
			say "points.";
		Now the last notified score is the score;
	if quest0 completed is true:
		end the story finally; [Win]

The simpler notify score changes rule substitutes for the notify score changes rule.

Rule for listing nondescript items:
	stop.

Rule for printing the banner text:
	say "[fixed letter spacing]";
	say "                    ________  ________  __    __  ________        [line break]";
	say "                   |        \|        \|  \  |  \|        \       [line break]";
	say "                    \$$$$$$$$| $$$$$$$$| $$  | $$ \$$$$$$$$       [line break]";
	say "                      | $$   | $$__     \$$\/  $$   | $$          [line break]";
	say "                      | $$   | $$  \     >$$  $$    | $$          [line break]";
	say "                      | $$   | $$$$$    /  $$$$\    | $$          [line break]";
	say "                      | $$   | $$_____ |  $$ \$$\   | $$          [line break]";
	say "                      | $$   | $$     \| $$  | $$   | $$          [line break]";
	say "                       \$$    \$$$$$$$$ \$$   \$$    \$$          [line break]";
	say "              __       __   ______   _______   __        _______  [line break]";
	say "             |  \  _  |  \ /      \ |       \ |  \      |       \ [line break]";
	say "             | $$ / \ | $$|  $$$$$$\| $$$$$$$\| $$      | $$$$$$$\[line break]";
	say "             | $$/  $\| $$| $$  | $$| $$__| $$| $$      | $$  | $$[line break]";
	say "             | $$  $$$\ $$| $$  | $$| $$    $$| $$      | $$  | $$[line break]";
	say "             | $$ $$\$$\$$| $$  | $$| $$$$$$$\| $$      | $$  | $$[line break]";
	say "             | $$$$  \$$$$| $$__/ $$| $$  | $$| $$_____ | $$__/ $$[line break]";
	say "             | $$$    \$$$ \$$    $$| $$  | $$| $$     \| $$    $$[line break]";
	say "              \$$      \$$  \$$$$$$  \$$   \$$ \$$$$$$$$ \$$$$$$$ [line break]";
	say "[variable letter spacing][line break]";
	say "[objective][line break]".

Include Basic Screen Effects by Emily Short.

Rule for printing the player's obituary:
	if story has ended finally:
		center "*** The End ***";
	else:
		center "*** You lost! ***";
	say paragraph break;
	if maximum score is -32768:
		say "You scored a total of [score] point[s], in [turn count] turn[s].";
	else:
		say "You scored [score] out of a possible [maximum score], in [turn count] turn[s].";
	[wait for any key;
	stop game abruptly;]
	rule succeeds.

Carry out requesting the score:
	if maximum score is -32768:
		say "You have so far scored [score] point[s], in [turn count] turn[s].";
	else:
		say "You have so far scored [score] out of a possible [maximum score], in [turn count] turn[s].";
	rule succeeds.

Rule for implicitly taking something (called target):
	if target is fixed in place:
		say "The [target] is fixed in place.";
	otherwise:
		say "You need to take the [target] first.";
		set pronouns from target;
	stop.

Does the player mean doing something:
	if the noun is not nothing and the second noun is nothing and the player's command matches the text printed name of the noun:
		it is likely;
	if the noun is nothing and the second noun is not nothing and the player's command matches the text printed name of the second noun:
		it is likely;
	if the noun is not nothing and the second noun is not nothing and the player's command matches the text printed name of the noun and the player's command matches the text printed name of the second noun:
		it is very likely.  [Handle action with two arguments.]

Printing the content of the room is an activity.
Rule for printing the content of the room:
	let R be the location of the player;
	say "Room contents:[line break]";
	list the contents of R, with newlines, indented, including all contents, with extra indentation.

Printing the content of the world is an activity.
Rule for printing the content of the world:
	let L be the list of the rooms;
	say "World: [line break]";
	repeat with R running through L:
		say "  [the internal name of R][line break]";
	repeat with R running through L:
		say "[the internal name of R]:[line break]";
		if the list of things in R is empty:
			say "  nothing[line break]";
		otherwise:
			list the contents of R, with newlines, indented, including all contents, with extra indentation.

Printing the content of the inventory is an activity.
Rule for printing the content of the inventory:
	say "You are carrying: ";
	list the contents of the player, as a sentence, giving inventory information, including all contents;
	say ".".

The print standard inventory rule is not listed in any rulebook.
Carry out taking inventory (this is the new print inventory rule):
	say "You are carrying: ";
	list the contents of the player, as a sentence, giving inventory information, including all contents;
	say ".".

Printing the content of nowhere is an activity.
Rule for printing the content of nowhere:
	say "Nowhere:[line break]";
	let L be the list of the off-stage things;
	repeat with thing running through L:
		say "  [thing][line break]";

Printing the things on the floor is an activity.
Rule for printing the things on the floor:
	let R be the location of the player;
	let L be the list of things in R;
	remove yourself from L;
	remove the list of containers from L;
	remove the list of supporters from L;
	remove the list of doors from L;
	if the number of entries in L is greater than 0:
		say "There is [L with indefinite articles] on the floor.";

After printing the name of something (called target) while
printing the content of the room
or printing the content of the world
or printing the content of the inventory
or printing the content of nowhere:
	follow the property-aggregation rules for the target.

The property-aggregation rules are an object-based rulebook.
The property-aggregation rulebook has a list of text called the tagline.

[At the moment, we only support "open/unlocked", "closed/unlocked" and "closed/locked" for doors and containers.]
[A first property-aggregation rule for an openable open thing (this is the mention open openables rule):
	add "open" to the tagline.

A property-aggregation rule for an openable closed thing (this is the mention closed openables rule):
	add "closed" to the tagline.

A property-aggregation rule for an lockable unlocked thing (this is the mention unlocked lockable rule):
	add "unlocked" to the tagline.

A property-aggregation rule for an lockable locked thing (this is the mention locked lockable rule):
	add "locked" to the tagline.]

A first property-aggregation rule for an openable lockable open unlocked thing (this is the mention open openables rule):
	add "open" to the tagline.

A property-aggregation rule for an openable lockable closed unlocked thing (this is the mention closed openables rule):
	add "closed" to the tagline.

A property-aggregation rule for an openable lockable closed locked thing (this is the mention locked openables rule):
	add "locked" to the tagline.

A property-aggregation rule for a lockable thing (called the lockable thing) (this is the mention matching key of lockable rule):
	let X be the matching key of the lockable thing;
	if X is not nothing:
		add "match [X]" to the tagline.

A property-aggregation rule for an edible off-stage thing (this is the mention eaten edible rule):
	add "eaten" to the tagline.

The last property-aggregation rule (this is the print aggregated properties rule):
	if the number of entries in the tagline is greater than 0:
		say " ([tagline])";
		rule succeeds;
	rule fails;

The objective part 0 is some text that varies. The objective part 0 is "Who's got a virtual machine and is about to play through an fast paced round of TextWorld? You do! Here is how to play! First step, take a trip west. Then, make an effort to travel west. Once you acco".
The objective part 1 is some text that varies. The objective part 1 is "mplish that, take a trip north. Next, attempt to travel west. Then, attempt to head north. With that accomplished, move north. Then, take the keycard from the saucepan in the kitchenette. That's it!".

An objective is some text that varies. The objective is "[objective part 0][objective part 1]".
Printing the objective is an action applying to nothing.
Carry out printing the objective:
	say "[objective]".

Understand "goal" as printing the objective.

The taking action has an object called previous locale (matched as "from").

Setting action variables for taking:
	now previous locale is the holder of the noun.

Report taking something from the location:
	say "You pick up [the noun] from the ground." instead.

Report taking something:
	say "You take [the noun] from [the previous locale]." instead.

Report dropping something:
	say "You drop [the noun] on the ground." instead.

The print state option is a truth state that varies.
The print state option is usually false.

Turning on the print state option is an action applying to nothing.
Carry out turning on the print state option:
	Now the print state option is true.

Turning off the print state option is an action applying to nothing.
Carry out turning off the print state option:
	Now the print state option is false.

Printing the state is an activity.
Rule for printing the state:
	let R be the location of the player;
	say "Room: [line break] [the internal name of R][line break]";
	[say "[line break]";
	carry out the printing the content of the room activity;]
	say "[line break]";
	carry out the printing the content of the world activity;
	say "[line break]";
	carry out the printing the content of the inventory activity;
	say "[line break]";
	carry out the printing the content of nowhere activity;
	say "[line break]".

Printing the entire state is an action applying to nothing.
Carry out printing the entire state:
	say "-=STATE START=-[line break]";
	carry out the printing the state activity;
	say "[line break]Score:[line break] [score]/[maximum score][line break]";
	say "[line break]Objective:[line break] [objective][line break]";
	say "[line break]Inventory description:[line break]";
	say "  You are carrying: [a list of things carried by the player].[line break]";
	say "[line break]Room description:[line break]";
	try looking;
	say "[line break]-=STATE STOP=-";

Every turn:
	if extra description command option is true:
		say "<description>";
		try looking;
		say "</description>";
	if extra inventory command option is true:
		say "<inventory>";
		try taking inventory;
		say "</inventory>";
	if extra score command option is true:
		say "<score>[line break][score][line break]</score>";
	if extra score command option is true:
		say "<moves>[line break][turn count][line break]</moves>";
	if print state option is true:
		try printing the entire state;

When play ends:
	if print state option is true:
		try printing the entire state;

After looking:
	carry out the printing the things on the floor activity.

Understand "print_state" as printing the entire state.
Understand "enable print state option" as turning on the print state option.
Understand "disable print state option" as turning off the print state option.

Before going through a closed door (called the blocking door):
	say "You have to open the [blocking door] first.";
	stop.

Before opening a locked door (called the locked door):
	let X be the matching key of the locked door;
	if X is nothing:
		say "The [locked door] is welded shut.";
	otherwise:
		say "You have to unlock the [locked door] with the [X] first.";
	stop.

Before opening a locked container (called the locked container):
	let X be the matching key of the locked container;
	if X is nothing:
		say "The [locked container] is welded shut.";
	otherwise:
		say "You have to unlock the [locked container] with the [X] first.";
	stop.

Displaying help message is an action applying to nothing.
Carry out displaying help message:
	say "[fixed letter spacing]Available commands:[line break]";
	say "  look:                describe the current room[line break]";
	say "  goal:                print the goal of this game[line break]";
	say "  inventory:           print player's inventory[line break]";
	say "  go <dir>:            move the player north, east, south or west[line break]";
	say "  examine ...:         examine something more closely[line break]";
	say "  eat ...:             eat edible food[line break]";
	say "  open ...:            open a door or a container[line break]";
	say "  close ...:           close a door or a container[line break]";
	say "  drop ...:            drop an object on the floor[line break]";
	say "  take ...:            take an object that is on the floor[line break]";
	say "  put ... on ...:      place an object on a supporter[line break]";
	say "  take ... from ...:   take an object from a container or a supporter[line break]";
	say "  insert ... into ...: place an object into a container[line break]";
	say "  lock ... with ...:   lock a door or a container with a key[line break]";
	say "  unlock ... with ...: unlock a door or a container with a key[line break]";

Understand "help" as displaying help message.

Taking all is an action applying to nothing.
Check taking all:
	say "You have to be more specific!";
	rule fails.

Understand "take all" as taking all.
Understand "get all" as taking all.
Understand "pick up all" as taking all.

Understand "take each" as taking all.
Understand "get each" as taking all.
Understand "pick up each" as taking all.

Understand "take everything" as taking all.
Understand "get everything" as taking all.
Understand "pick up everything" as taking all.

The extra description command option is a truth state that varies.
The extra description command option is usually false.

Turning on the extra description command option is an action applying to nothing.
Carry out turning on the extra description command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra description command option is true.

Understand "tw-extra-infos description" as turning on the extra description command option.

The extra inventory command option is a truth state that varies.
The extra inventory command option is usually false.

Turning on the extra inventory command option is an action applying to nothing.
Carry out turning on the extra inventory command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra inventory command option is true.

Understand "tw-extra-infos inventory" as turning on the extra inventory command option.

The extra score command option is a truth state that varies.
The extra score command option is usually false.

Turning on the extra score command option is an action applying to nothing.
Carry out turning on the extra score command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra score command option is true.

Understand "tw-extra-infos score" as turning on the extra score command option.

The extra moves command option is a truth state that varies.
The extra moves command option is usually false.

Turning on the extra moves command option is an action applying to nothing.
Carry out turning on the extra moves command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra moves command option is true.

Understand "tw-extra-infos moves" as turning on the extra moves command option.

To trace the actions:
	(- trace_actions = 1; -).

Tracing the actions is an action applying to nothing.
Carry out tracing the actions:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	trace the actions;

Understand "tw-trace-actions" as tracing the actions.

The restrict commands option is a truth state that varies.
The restrict commands option is usually false.

Turning on the restrict commands option is an action applying to nothing.
Carry out turning on the restrict commands option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the restrict commands option is true.

Understand "restrict commands" as turning on the restrict commands option.

The taking allowed flag is a truth state that varies.
The taking allowed flag is usually false.

Before removing something from something:
	now the taking allowed flag is true.

After removing something from something:
	now the taking allowed flag is false.

Before taking a thing (called the object) when the object is on a supporter (called the supporter):
	if the restrict commands option is true and taking allowed flag is false:
		say "Can't see any [object] on the floor! Try taking the [object] from the [supporter] instead.";
		rule fails.

Before of taking a thing (called the object) when the object is in a container (called the container):
	if the restrict commands option is true and taking allowed flag is false:
		say "Can't see any [object] on the floor! Try taking the [object] from the [container] instead.";
		rule fails.

Understand "take [something]" as removing it from.

Rule for supplying a missing second noun while removing:
	if restrict commands option is false and noun is on a supporter (called the supporter):
		now the second noun is the supporter;
	else if restrict commands option is false and noun is in a container (called the container):
		now the second noun is the container;
	else:
		try taking the noun;
		say ""; [Needed to avoid printing a default message.]

The version number is always 1.

Reporting the version number is an action applying to nothing.
Carry out reporting the version number:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	say "[version number]".

Understand "tw-print version" as reporting the version number.

Reporting max score is an action applying to nothing.
Carry out reporting max score:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	if maximum score is -32768:
		say "infinity";
	else:
		say "[maximum score]".

Understand "tw-print max_score" as reporting max score.

To print id of (something - thing):
	(- print {something}, "^"; -).

Printing the id of player is an action applying to nothing.
Carry out printing the id of player:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	print id of player.

Printing the id of EndOfObject is an action applying to nothing.
Carry out printing the id of EndOfObject:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	print id of EndOfObject.

Understand "tw-print player id" as printing the id of player.
Understand "tw-print EndOfObject id" as printing the id of EndOfObject.

There is a EndOfObject.

