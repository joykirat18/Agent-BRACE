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


The r_1 and the r_0 and the r_10 and the r_11 and the r_12 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_8 and the r_9 and the r_13 and the r_19 and the r_7 are rooms.

Understand "basement" as r_1.
The internal name of r_1 is "basement".
The printed name of r_1 is "-= Basement =-".
The basement part 0 is some text that varies. The basement part 0 is "If you're wondering why everything seems so typical all of a sudden, it's because you've just walked into the basement.

 You see a counter. [if there is something on the s_0]You see [a list of things on the s_0] on the counter.[end if]".
The basement part 1 is some text that varies. The basement part 1 is "[if there is nothing on the s_0]But oh no! there's nothing on this piece of garbage.[end if]".
The basement part 2 is some text that varies. The basement part 2 is " Oh, great. Here's a shelf. [if there is something on the s_1]On the shelf you see [a list of things on the s_1].[end if]".
The basement part 3 is some text that varies. The basement part 3 is "[if there is nothing on the s_1]But the thing is empty, unfortunately.[end if]".
The basement part 4 is some text that varies. The basement part 4 is "

There is an exit to the north. Don't worry, it is unblocked. You don't like doors? Why not try going south, that entranceway is unguarded. You need an unblocked exit? You should try going west.".
The description of r_1 is "[basement part 0][basement part 1][basement part 2][basement part 3][basement part 4]".

The r_0 is mapped west of r_1.
The r_2 is mapped south of r_1.
The r_13 is mapped north of r_1.
Understand "launderette" as r_0.
The internal name of r_0 is "launderette".
The printed name of r_0 is "-= Launderette =-".
The launderette part 0 is some text that varies. The launderette part 0 is "You arrive in a launderette. An ordinary kind of place. You start to take note of what's in the room.

 You scan the room for a dresser, and you find a dresser.[if c_0 is open and there is something in the c_0] The dresser contains [a list of things in the c_0]![end if]".
The launderette part 1 is some text that varies. The launderette part 1 is "[if c_0 is open and the c_0 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The launderette part 2 is some text that varies. The launderette part 2 is " As if things weren't amazing enough already, you can even see a bench. The bench is standard.[if there is something on the s_2] On the bench you make out [a list of things on the s_2].[end if]".
The launderette part 3 is some text that varies. The launderette part 3 is "[if there is nothing on the s_2] But the thing is empty. What, you think everything in TextWorld should have stuff on it?[end if]".
The launderette part 4 is some text that varies. The launderette part 4 is "

There is an unblocked exit to the east. There is an unblocked exit to the south.".
The description of r_0 is "[launderette part 0][launderette part 1][launderette part 2][launderette part 3][launderette part 4]".

The r_3 is mapped south of r_0.
The r_1 is mapped east of r_0.
Understand "recreation zone" as r_10.
The internal name of r_10 is "recreation zone".
The printed name of r_10 is "-= Recreation Zone =-".
The recreation zone part 0 is some text that varies. The recreation zone part 0 is "Well I'll be, you are in the place we're calling the recreation zone.



 There is [if d_6 is open]an open[otherwise]a closed[end if]".
The recreation zone part 1 is some text that varies. The recreation zone part 1 is " passageway leading north. There is an exit to the east. Don't worry, it is unblocked. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_10 is "[recreation zone part 0][recreation zone part 1]".

The r_11 is mapped west of r_10.
north of r_10 and south of r_8 is a door called d_6.
The r_12 is mapped east of r_10.
Understand "lounge" as r_11.
The internal name of r_11 is "lounge".
The printed name of r_11 is "-= Lounge =-".
The lounge part 0 is some text that varies. The lounge part 0 is "You find yourself in a lounge. A typical one.

 You see a mantle. The mantle is standard.[if there is something on the s_3] On the mantle you see [a list of things on the s_3].[end if]".
The lounge part 1 is some text that varies. The lounge part 1 is "[if there is nothing on the s_3] But the thing hasn't got anything on it. Hm. Oh well[end if]".
The lounge part 2 is some text that varies. The lounge part 2 is "

There is an unblocked exit to the east.".
The description of r_11 is "[lounge part 0][lounge part 1][lounge part 2]".

The r_10 is mapped east of r_11.
Understand "sauna" as r_12.
The internal name of r_12 is "sauna".
The printed name of r_12 is "-= Sauna =-".
The sauna part 0 is some text that varies. The sauna part 0 is "You are in a standard kind of place. That is to say, you're in a sauna.

 What's that over there? It looks like it's a cabinet.[if c_1 is open and there is something in the c_1] The cabinet contains [a list of things in the c_1].[end if]".
The sauna part 1 is some text that varies. The sauna part 1 is "[if c_1 is open and the c_1 contains nothing] The cabinet is empty, what a horrible day![end if]".
The sauna part 2 is some text that varies. The sauna part 2 is " You can see a board. The board is standard.[if there is something on the s_4] On the board you see [a list of things on the s_4]. There's something strange about this being here, but you can't put your finger on it.[end if]".
The sauna part 3 is some text that varies. The sauna part 3 is "[if there is nothing on the s_4] Unfortunately, there isn't a thing on it. You think about smashing the board to bits, throwing the bits in the dump, etc, until you get bored.[end if]".
The sauna part 4 is some text that varies. The sauna part 4 is "

You need an unblocked exit? You should try going north. You need an unblocked exit? You should try going west.".
The description of r_12 is "[sauna part 0][sauna part 1][sauna part 2][sauna part 3][sauna part 4]".

The r_10 is mapped west of r_12.
The r_6 is mapped north of r_12.
Understand "shower" as r_14.
The internal name of r_14 is "shower".
The printed name of r_14 is "-= Shower =-".
The shower part 0 is some text that varies. The shower part 0 is "You find yourself in a shower. A typical one.

 You make out a drawer.[if c_2 is open and there is something in the c_2] The drawer contains [a list of things in the c_2]. Wow, check out the price tag on the drawer! Three hundred dollars![end if]".
The shower part 1 is some text that varies. The shower part 1 is "[if c_2 is open and the c_2 contains nothing] What a letdown! The drawer is empty![end if]".
The shower part 2 is some text that varies. The shower part 2 is "

You don't like doors? Why not try going north, that entranceway is unguarded. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_14 is "[shower part 0][shower part 1][shower part 2]".

The r_15 is mapped west of r_14.
The r_4 is mapped north of r_14.
Understand "kitchenette" as r_15.
The internal name of r_15 is "kitchenette".
The printed name of r_15 is "-= Kitchenette =-".
The kitchenette part 0 is some text that varies. The kitchenette part 0 is "Well, here we are in the kitchenette. You decide to start listing off everything you see in the room, as if you were in a text adventure.

 You can make out a chest.[if c_3 is open and there is something in the c_3] The chest contains [a list of things in the c_3].[end if]".
The kitchenette part 1 is some text that varies. The kitchenette part 1 is "[if c_3 is open and the c_3 contains nothing] The chest is empty! What a waste of a day![end if]".
The kitchenette part 2 is some text that varies. The kitchenette part 2 is " You can see a platter. The platter is usual.[if there is something on the s_5] On the platter you see [a list of things on the s_5]. You idly wonder how they came up with the name TextWorld for this place. It's pretty fitting.[end if]".
The kitchenette part 3 is some text that varies. The kitchenette part 3 is "[if there is nothing on the s_5] But there isn't a thing on it. What, you think everything in TextWorld should have stuff on it?[end if]".
The kitchenette part 4 is some text that varies. The kitchenette part 4 is "

You need an unguarded exit? You should try going east. You don't like doors? Why not try going north, that entranceway is unguarded.".
The description of r_15 is "[kitchenette part 0][kitchenette part 1][kitchenette part 2][kitchenette part 3][kitchenette part 4]".

The r_5 is mapped north of r_15.
The r_14 is mapped east of r_15.
Understand "bathroom" as r_16.
The internal name of r_16 is "bathroom".
The printed name of r_16 is "-= Bathroom =-".
The bathroom part 0 is some text that varies. The bathroom part 0 is "Well, here we are in a bathroom.



 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The bathroom part 1 is some text that varies. The bathroom part 1 is " gateway leading south. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The bathroom part 2 is some text that varies. The bathroom part 2 is " door leading west.".
The description of r_16 is "[bathroom part 0][bathroom part 1][bathroom part 2]".

west of r_16 and east of r_17 is a door called d_1.
south of r_16 and north of r_7 is a door called d_2.
Understand "bar" as r_17.
The internal name of r_17 is "bar".
The printed name of r_17 is "-= Bar =-".
The bar part 0 is some text that varies. The bar part 0 is "You're now in the bar.

 You can make out a suitcase. I mean, just wow! Isn't TextWorld just the best?[if c_4 is open and there is something in the c_4] The suitcase contains [a list of things in the c_4]. I mean, just wow! Isn't TextWorld just the best?[end if]".
The bar part 1 is some text that varies. The bar part 1 is "[if c_4 is open and the c_4 contains nothing] The suitcase is empty! What a waste of a day![end if]".
The bar part 2 is some text that varies. The bar part 2 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The bar part 3 is some text that varies. The bar part 3 is " door leading east. There is [if d_0 is open]an open[otherwise]a closed[end if]".
The bar part 4 is some text that varies. The bar part 4 is " hatch leading west.".
The description of r_17 is "[bar part 0][bar part 1][bar part 2][bar part 3][bar part 4]".

west of r_17 and east of r_18 is a door called d_0.
east of r_17 and west of r_16 is a door called d_1.
Understand "cookery" as r_18.
The internal name of r_18 is "cookery".
The printed name of r_18 is "-= Cookery =-".
The cookery part 0 is some text that varies. The cookery part 0 is "You find yourself in a cookery. A normal kind of place. Okay, just remember what you're here to do, and everything will go great.



 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The cookery part 1 is some text that varies. The cookery part 1 is " hatch leading east. There is an exit to the north. Don't worry, it is unblocked.".
The description of r_18 is "[cookery part 0][cookery part 1]".

The r_19 is mapped north of r_18.
east of r_18 and west of r_17 is a door called d_0.
Understand "cookhouse" as r_2.
The internal name of r_2 is "cookhouse".
The printed name of r_2 is "-= Cookhouse =-".
The cookhouse part 0 is some text that varies. The cookhouse part 0 is "Okay, so you're in a cookhouse, cool, but is it standard? You better believe it is.

 You make out a bowl. [if there is something on the s_6]On the bowl you see [a list of things on the s_6].[end if]".
The cookhouse part 1 is some text that varies. The cookhouse part 1 is "[if there is nothing on the s_6]But the thing is empty, unfortunately.[end if]".
The cookhouse part 2 is some text that varies. The cookhouse part 2 is "

You don't like doors? Why not try going north, that entranceway is unguarded. You need an unblocked exit? You should try going south. You need an unblocked exit? You should try going west.".
The description of r_2 is "[cookhouse part 0][cookhouse part 1][cookhouse part 2]".

The r_3 is mapped west of r_2.
The r_4 is mapped south of r_2.
The r_1 is mapped north of r_2.
Understand "laundromat" as r_3.
The internal name of r_3 is "laundromat".
The printed name of r_3 is "-= Laundromat =-".
The laundromat part 0 is some text that varies. The laundromat part 0 is "Well, here we are in the laundromat. You begin to take stock of what's in the room.



You don't like doors? Why not try going east, that entranceway is unguarded. You don't like doors? Why not try going north, that entranceway is unblocked. There is an unblocked exit to the south.".
The description of r_3 is "[laundromat part 0]".

The r_5 is mapped south of r_3.
The r_0 is mapped north of r_3.
The r_2 is mapped east of r_3.
Understand "cellar" as r_4.
The internal name of r_4 is "cellar".
The printed name of r_4 is "-= Cellar =-".
The cellar part 0 is some text that varies. The cellar part 0 is "You've entered a cellar.

 You can make out a toolbox.[if c_5 is open and there is something in the c_5] The toolbox contains [a list of things in the c_5].[end if]".
The cellar part 1 is some text that varies. The cellar part 1 is "[if c_5 is open and the c_5 contains nothing] The toolbox is empty, what a horrible day![end if]".
The cellar part 2 is some text that varies. The cellar part 2 is "

You need an unblocked exit? You should try going north. You don't like doors? Why not try going south, that entranceway is unguarded. There is an unguarded exit to the west.".
The description of r_4 is "[cellar part 0][cellar part 1][cellar part 2]".

The r_5 is mapped west of r_4.
The r_14 is mapped south of r_4.
The r_2 is mapped north of r_4.
Understand "spare room" as r_5.
The internal name of r_5 is "spare room".
The printed name of r_5 is "-= Spare Room =-".
The spare room part 0 is some text that varies. The spare room part 0 is "You've entered a spare room. Okay, just remember what you're here to do, and everything will go great.

 You make out [if c_6 is locked]a locked[else if c_6 is open]an opened[otherwise]a closed[end if]".
The spare room part 1 is some text that varies. The spare room part 1 is " trunk right there by you.[if c_6 is open and there is something in the c_6] The trunk contains [a list of things in the c_6].[end if]".
The spare room part 2 is some text that varies. The spare room part 2 is "[if c_6 is open and the c_6 contains nothing] What a letdown! The trunk is empty![end if]".
The spare room part 3 is some text that varies. The spare room part 3 is " You make out [if c_7 is locked]a locked[else if c_7 is open]an opened[otherwise]a closed[end if]".
The spare room part 4 is some text that varies. The spare room part 4 is " coffer.[if c_7 is open and there is something in the c_7] The coffer contains [a list of things in the c_7].[end if]".
The spare room part 5 is some text that varies. The spare room part 5 is "[if c_7 is open and the c_7 contains nothing] The coffer is empty! What a waste of a day![end if]".
The spare room part 6 is some text that varies. The spare room part 6 is "

 There is [if d_5 is open]an open[otherwise]a closed[end if]".
The spare room part 7 is some text that varies. The spare room part 7 is " gate leading west. You don't like doors? Why not try going east, that entranceway is unguarded. You don't like doors? Why not try going north, that entranceway is unguarded. There is an unguarded exit to the south.".
The description of r_5 is "[spare room part 0][spare room part 1][spare room part 2][spare room part 3][spare room part 4][spare room part 5][spare room part 6][spare room part 7]".

west of r_5 and east of r_6 is a door called d_5.
The r_15 is mapped south of r_5.
The r_3 is mapped north of r_5.
The r_4 is mapped east of r_5.
Understand "restroom" as r_6.
The internal name of r_6 is "restroom".
The printed name of r_6 is "-= Restroom =-".
The restroom part 0 is some text that varies. The restroom part 0 is "You've just sauntered into a restroom.

 You can make out a rack. [if there is something on the s_7]On the rack you can make out [a list of things on the s_7]. Something scurries by right in the corner of your eye. Probably nothing.[end if]".
The restroom part 1 is some text that varies. The restroom part 1 is "[if there is nothing on the s_7]However, the rack, like an empty rack, has nothing on it. What, you think everything in TextWorld should have stuff on it?[end if]".
The restroom part 2 is some text that varies. The restroom part 2 is "

 There is [if d_5 is open]an open[otherwise]a closed[end if]".
The restroom part 3 is some text that varies. The restroom part 3 is " gate leading east. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The restroom part 4 is some text that varies. The restroom part 4 is " portal leading north. There is [if d_4 is open]an open[otherwise]a closed[end if]".
The restroom part 5 is some text that varies. The restroom part 5 is " beech gate leading west. You need an unblocked exit? You should try going south.".
The description of r_6 is "[restroom part 0][restroom part 1][restroom part 2][restroom part 3][restroom part 4][restroom part 5]".

west of r_6 and east of r_8 is a door called d_4.
The r_12 is mapped south of r_6.
north of r_6 and south of r_7 is a door called d_3.
east of r_6 and west of r_5 is a door called d_5.
Understand "pantry" as r_8.
The internal name of r_8 is "pantry".
The printed name of r_8 is "-= Pantry =-".
The pantry part 0 is some text that varies. The pantry part 0 is "I am sorry to announce that you are now in the pantry. You begin to take stock of what's in the room.

 You can make out a stand. The stand is usual.[if there is something on the s_8] On the stand you see [a list of things on the s_8].[end if]".
The pantry part 1 is some text that varies. The pantry part 1 is "[if there is nothing on the s_8] Looks like someone's already been here and taken everything off it, though. Aw, here you were, all excited for there to be things on it![end if]".
The pantry part 2 is some text that varies. The pantry part 2 is "

 There is [if d_4 is open]an open[otherwise]a closed[end if]".
The pantry part 3 is some text that varies. The pantry part 3 is " beech gate leading east. There is [if d_6 is open]an open[otherwise]a closed[end if]".
The pantry part 4 is some text that varies. The pantry part 4 is " passageway leading south. There is an unguarded exit to the west.".
The description of r_8 is "[pantry part 0][pantry part 1][pantry part 2][pantry part 3][pantry part 4]".

The r_9 is mapped west of r_8.
south of r_8 and north of r_10 is a door called d_6.
east of r_8 and west of r_6 is a door called d_4.
Understand "canteen" as r_9.
The internal name of r_9 is "canteen".
The printed name of r_9 is "-= Canteen =-".
The canteen part 0 is some text that varies. The canteen part 0 is "You've entered a canteen. You try to gain information on your surroundings by using a technique you call 'looking.'

 You see a chair. [if there is something on the s_9]You see [a list of things on the s_9] on the chair.[end if]".
The canteen part 1 is some text that varies. The canteen part 1 is "[if there is nothing on the s_9]But the thing hasn't got anything on it.[end if]".
The canteen part 2 is some text that varies. The canteen part 2 is "

You don't like doors? Why not try going east, that entranceway is unguarded.".
The description of r_9 is "[canteen part 0][canteen part 1][canteen part 2]".

The r_8 is mapped east of r_9.
Understand "chamber" as r_13.
The internal name of r_13 is "chamber".
The printed name of r_13 is "-= Chamber =-".
The chamber part 0 is some text that varies. The chamber part 0 is "You arrive in a chamber. A standard one.

 You hear a noise behind you and spin around, but you can't see anything other than a safe.[if c_8 is open and there is something in the c_8] The safe contains [a list of things in the c_8].[end if]".
The chamber part 1 is some text that varies. The chamber part 1 is "[if c_8 is open and the c_8 contains nothing] What a letdown! The safe is empty![end if]".
The chamber part 2 is some text that varies. The chamber part 2 is "

You don't like doors? Why not try going south, that entranceway is unguarded.".
The description of r_13 is "[chamber part 0][chamber part 1][chamber part 2]".

The r_1 is mapped south of r_13.
Understand "parlor" as r_19.
The internal name of r_19 is "parlor".
The printed name of r_19 is "-= Parlor =-".
The parlor part 0 is some text that varies. The parlor part 0 is "You are in a parlor. An usual kind of place.



You need an unguarded exit? You should try going south.".
The description of r_19 is "[parlor part 0]".

The r_18 is mapped south of r_19.
Understand "closet" as r_7.
The internal name of r_7 is "closet".
The printed name of r_7 is "-= Closet =-".
The closet part 0 is some text that varies. The closet part 0 is "You find yourself in a closet. An usual one.

 If you haven't noticed it already, there seems to be something there by the wall, it's a table. The table is ordinary.[if there is something on the s_10] On the table you make out [a list of things on the s_10].[end if]".
The closet part 1 is some text that varies. The closet part 1 is "[if there is nothing on the s_10] But the thing is empty. What, you think everything in TextWorld should have stuff on it?[end if]".
The closet part 2 is some text that varies. The closet part 2 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The closet part 3 is some text that varies. The closet part 3 is " gateway leading north. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The closet part 4 is some text that varies. The closet part 4 is " portal leading south.".
The description of r_7 is "[closet part 0][closet part 1][closet part 2][closet part 3][closet part 4]".

south of r_7 and north of r_6 is a door called d_3.
north of r_7 and south of r_16 is a door called d_2.

The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 are containers.
The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 are privately-named.
The d_6 and the d_1 and the d_2 and the d_0 and the d_5 and the d_3 and the d_4 are doors.
The d_6 and the d_1 and the d_2 and the d_0 and the d_5 and the d_3 and the d_4 are privately-named.
The f_0 are foods.
The f_0 are privately-named.
The k_0 are keys.
The k_0 are privately-named.
The r_1 and the r_0 and the r_10 and the r_11 and the r_12 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_8 and the r_9 and the r_13 and the r_19 and the r_7 are rooms.
The r_1 and the r_0 and the r_10 and the r_11 and the r_12 and the r_14 and the r_15 and the r_16 and the r_17 and the r_18 and the r_2 and the r_3 and the r_4 and the r_5 and the r_6 and the r_8 and the r_9 and the r_13 and the r_19 and the r_7 are privately-named.
The s_0 and the s_1 and the s_10 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are supporters.
The s_0 and the s_1 and the s_10 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are privately-named.

The description of d_6 is "The passageway looks towering. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_6 is "passageway".
Understand "passageway" as d_6.
The d_6 is open.
The description of d_1 is "it is what it is, a door [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_1 is "door".
Understand "door" as d_1.
The d_1 is open.
The description of d_2 is "it's a commanding gateway [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_2 is "gateway".
Understand "gateway" as d_2.
The d_2 is open.
The description of d_0 is "it's a noble hatch [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_0 is "hatch".
Understand "hatch" as d_0.
The d_0 is open.
The description of d_5 is "it is what it is, a gate [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_5 is "gate".
Understand "gate" as d_5.
The d_5 is open.
The description of d_3 is "it is what it is, a portal [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_3 is "portal".
Understand "portal" as d_3.
The d_3 is open.
The description of d_4 is "The beech gate looks robust. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_4 is "beech gate".
Understand "beech gate" as d_4.
Understand "beech" as d_4.
Understand "gate" as d_4.
The d_4 is open.
The description of c_0 is "The dresser looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_0 is "dresser".
Understand "dresser" as c_0.
The c_0 is in r_0.
The c_0 is locked.
The description of c_1 is "The cabinet looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_1 is "cabinet".
Understand "cabinet" as c_1.
The c_1 is in r_12.
The c_1 is closed.
The description of c_2 is "The drawer looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_2 is "drawer".
Understand "drawer" as c_2.
The c_2 is in r_14.
The c_2 is locked.
The description of c_3 is "The chest looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "chest".
Understand "chest" as c_3.
The c_3 is in r_15.
The c_3 is open.
The description of c_4 is "The suitcase looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_4 is "suitcase".
Understand "suitcase" as c_4.
The c_4 is in r_17.
The c_4 is locked.
The description of c_5 is "The toolbox looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_5 is "toolbox".
Understand "toolbox" as c_5.
The c_5 is in r_4.
The c_5 is closed.
The description of c_6 is "The trunk looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_6 is "trunk".
Understand "trunk" as c_6.
The c_6 is in r_5.
The c_6 is locked.
The description of c_7 is "The coffer looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_7 is "coffer".
Understand "coffer" as c_7.
The c_7 is in r_5.
The c_7 is closed.
The description of c_8 is "The safe looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_8 is "safe".
Understand "safe" as c_8.
The c_8 is in r_13.
The c_8 is locked.
The description of f_0 is "The gummy bear looks delectable.".
The printed name of f_0 is "gummy bear".
Understand "gummy bear" as f_0.
Understand "gummy" as f_0.
Understand "bear" as f_0.
The f_0 is in r_6.
The description of k_0 is "The latchkey looks useful".
The printed name of k_0 is "latchkey".
Understand "latchkey" as k_0.
The k_0 is in r_6.
The description of s_0 is "The counter is stable.".
The printed name of s_0 is "counter".
Understand "counter" as s_0.
The s_0 is in r_1.
The description of s_1 is "The shelf is durable.".
The printed name of s_1 is "shelf".
Understand "shelf" as s_1.
The s_1 is in r_1.
The description of s_10 is "The table is durable.".
The printed name of s_10 is "table".
Understand "table" as s_10.
The s_10 is in r_7.
The description of s_2 is "The bench is stable.".
The printed name of s_2 is "bench".
Understand "bench" as s_2.
The s_2 is in r_0.
The description of s_3 is "The mantle is an unstable piece of garbage.".
The printed name of s_3 is "mantle".
Understand "mantle" as s_3.
The s_3 is in r_11.
The description of s_4 is "The board is solid.".
The printed name of s_4 is "board".
Understand "board" as s_4.
The s_4 is in r_12.
The description of s_5 is "The platter is undependable.".
The printed name of s_5 is "platter".
Understand "platter" as s_5.
The s_5 is in r_15.
The description of s_6 is "The bowl is durable.".
The printed name of s_6 is "bowl".
Understand "bowl" as s_6.
The s_6 is in r_2.
The description of s_7 is "The rack is an unstable piece of junk.".
The printed name of s_7 is "rack".
Understand "rack" as s_7.
The s_7 is in r_6.
The description of s_8 is "The stand is balanced.".
The printed name of s_8 is "stand".
Understand "stand" as s_8.
The s_8 is in r_8.
The description of s_9 is "The chair is balanced.".
The printed name of s_9 is "chair".
Understand "chair" as s_9.
The s_9 is in r_9.


The player is in r_4.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.

Test quest0_0 with "go south / go west / go north / go west / take gummy bear"

Every turn:
	if quest0 completed is true:
		do nothing;
	else if The player carries the k_0:
		end the story; [Lost]
	else if The player is in r_6 and The player carries the f_0:
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

The objective part 0 is some text that varies. The objective part 0 is "Hey, thanks for coming over to the TextWorld today, there is something I need you to do for me. First of all, make an attempt to head south. And then, attempt to move west. With that accomplished, ven".
The objective part 1 is some text that varies. The objective part 1 is "ture north. With that done, make an effort to head west. With that done, pick-up the gummy bear from the floor of the restroom. And if you do that, you're the winner!".

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

