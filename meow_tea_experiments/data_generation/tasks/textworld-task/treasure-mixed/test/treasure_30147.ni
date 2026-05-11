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


The r_10 and the r_0 and the r_12 and the r_9 and the r_13 and the r_14 and the r_15 and the r_17 and the r_16 and the r_19 and the r_18 and the r_4 and the r_2 and the r_5 and the r_1 and the r_6 and the r_8 and the r_11 and the r_3 and the r_7 are rooms.

Understand "bedchamber" as r_10.
The internal name of r_10 is "bedchamber".
The printed name of r_10 is "-= Bedchamber =-".
The bedchamber part 0 is some text that varies. The bedchamber part 0 is "Well, here we are in the bedchamber.

 You can make out a couch. [if there is something on the s_0]You see [a list of things on the s_0] on the couch.[end if]".
The bedchamber part 1 is some text that varies. The bedchamber part 1 is "[if there is nothing on the s_0]But oh no! there's nothing on this piece of garbage. Sometimes, just sometimes, TextWorld can just be the worst.[end if]".
The bedchamber part 2 is some text that varies. The bedchamber part 2 is "

There is an exit to the east. Don't worry, it is unguarded. You need an unblocked exit? You should try going south. You need an unguarded exit? You should try going west.".
The description of r_10 is "[bedchamber part 0][bedchamber part 1][bedchamber part 2]".

The r_0 is mapped west of r_10.
The r_11 is mapped south of r_10.
The r_8 is mapped east of r_10.
Understand "attic" as r_0.
The internal name of r_0 is "attic".
The printed name of r_0 is "-= Attic =-".
The attic part 0 is some text that varies. The attic part 0 is "You've just shown up in an attic. You begin to take stock of what's here.

 You see a stand. [if there is something on the s_1]You see [a list of things on the s_1] on the stand.[end if]".
The attic part 1 is some text that varies. The attic part 1 is "[if there is nothing on the s_1]But there isn't a thing on it.[end if]".
The attic part 2 is some text that varies. The attic part 2 is "

You don't like doors? Why not try going east, that entranceway is unblocked. You don't like doors? Why not try going north, that entranceway is unguarded.".
The description of r_0 is "[attic part 0][attic part 1][attic part 2]".

The r_1 is mapped north of r_0.
The r_10 is mapped east of r_0.
Understand "pantry" as r_12.
The internal name of r_12 is "pantry".
The printed name of r_12 is "-= Pantry =-".
The pantry part 0 is some text that varies. The pantry part 0 is "Well, here we are in a pantry.

 You can see a rack. The rack is ordinary.[if there is something on the s_2] On the rack you see [a list of things on the s_2].[end if]".
The pantry part 1 is some text that varies. The pantry part 1 is "[if there is nothing on the s_2] But the thing hasn't got anything on it. It would have been so cool if there was stuff on the rack.[end if]".
The pantry part 2 is some text that varies. The pantry part 2 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The pantry part 3 is some text that varies. The pantry part 3 is " gate leading north. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The pantry part 4 is some text that varies. The pantry part 4 is " gateway leading west. There is an unguarded exit to the east.".
The description of r_12 is "[pantry part 0][pantry part 1][pantry part 2][pantry part 3][pantry part 4]".

west of r_12 and east of r_9 is a door called d_3.
north of r_12 and south of r_15 is a door called d_2.
The r_13 is mapped east of r_12.
Understand "studio" as r_9.
The internal name of r_9 is "studio".
The printed name of r_9 is "-= Studio =-".
The studio part 0 is some text that varies. The studio part 0 is "You are in a studio. A normal one.

 You can see [if c_0 is locked]a locked[else if c_0 is open]an opened[otherwise]a closed[end if]".
The studio part 1 is some text that varies. The studio part 1 is " portmanteau.[if c_0 is open and there is something in the c_0] The portmanteau contains [a list of things in the c_0].[end if]".
The studio part 2 is some text that varies. The studio part 2 is "[if c_0 is open and the c_0 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The studio part 3 is some text that varies. The studio part 3 is "

 There is [if d_3 is open]an open[otherwise]a closed[end if]".
The studio part 4 is some text that varies. The studio part 4 is " gateway leading east. You need an unblocked exit? You should try going north. You need an unblocked exit? You should try going west.".
The description of r_9 is "[studio part 0][studio part 1][studio part 2][studio part 3][studio part 4]".

The r_11 is mapped west of r_9.
The r_8 is mapped north of r_9.
east of r_9 and west of r_12 is a door called d_3.
Understand "garage" as r_13.
The internal name of r_13 is "garage".
The printed name of r_13 is "-= Garage =-".
The garage part 0 is some text that varies. The garage part 0 is "Look at you, bigshot, walking into a garage like it isn't some huge deal.

 You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a coffer.[if c_1 is open and there is something in the c_1] The coffer contains [a list of things in the c_1].[end if]".
The garage part 1 is some text that varies. The garage part 1 is "[if c_1 is open and the c_1 contains nothing] The coffer is empty, what a horrible day![end if]".
The garage part 2 is some text that varies. The garage part 2 is " You can see a counter. Make a note of this, you might have to put stuff on or in it later on. The counter is normal.[if there is something on the s_3] On the counter you can make out [a list of things on the s_3].[end if]".
The garage part 3 is some text that varies. The garage part 3 is "[if there is nothing on the s_3] Looks like someone's already been here and taken everything off it, though. You move on, clearly infuriated by your TextWorld experience.[end if]".
The garage part 4 is some text that varies. The garage part 4 is "

There is an exit to the north. Don't worry, it is unguarded. You need an unblocked exit? You should try going west.".
The description of r_13 is "[garage part 0][garage part 1][garage part 2][garage part 3][garage part 4]".

The r_12 is mapped west of r_13.
The r_14 is mapped north of r_13.
Understand "office" as r_14.
The internal name of r_14 is "office".
The printed name of r_14 is "-= Office =-".
The office part 0 is some text that varies. The office part 0 is "Of every office you could have shown up in, you had to show up in a standard one.

 Oh wow! Is that what I think it is? It is! It's a bureau.[if c_2 is open and there is something in the c_2] The bureau contains [a list of things in the c_2].[end if]".
The office part 1 is some text that varies. The office part 1 is "[if c_2 is open and the c_2 contains nothing] The bureau is empty! What a waste of a day![end if]".
The office part 2 is some text that varies. The office part 2 is "

There is an exit to the south. Don't worry, it is unblocked. There is an unblocked exit to the west.".
The description of r_14 is "[office part 0][office part 1][office part 2]".

The r_15 is mapped west of r_14.
The r_13 is mapped south of r_14.
Understand "kitchen" as r_15.
The internal name of r_15 is "kitchen".
The printed name of r_15 is "-= Kitchen =-".
The kitchen part 0 is some text that varies. The kitchen part 0 is "Well, here we are in the kitchen.

 As if things weren't amazing enough already, you can even see a chair. What a coincidence, weren't you just thinking about a chair? [if there is something on the s_4]You see [a list of things on the s_4] on the chair.[end if]".
The kitchen part 1 is some text that varies. The kitchen part 1 is "[if there is nothing on the s_4]Looks like someone's already been here and taken everything off it, though. Aw, and here you were, all excited for there to be things on it![end if]".
The kitchen part 2 is some text that varies. The kitchen part 2 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The kitchen part 3 is some text that varies. The kitchen part 3 is " portal leading north. There is [if d_2 is open]an open[otherwise]a closed[end if]".
The kitchen part 4 is some text that varies. The kitchen part 4 is " gate leading south. You don't like doors? Why not try going east, that entranceway is unblocked.".
The description of r_15 is "[kitchen part 0][kitchen part 1][kitchen part 2][kitchen part 3][kitchen part 4]".

south of r_15 and north of r_12 is a door called d_2.
north of r_15 and south of r_16 is a door called d_1.
The r_14 is mapped east of r_15.
Understand "cubicle" as r_17.
The internal name of r_17 is "cubicle".
The printed name of r_17 is "-= Cubicle =-".
The cubicle part 0 is some text that varies. The cubicle part 0 is "You've entered a cubicle.

 You can see a toolbox.[if c_3 is open and there is something in the c_3] The toolbox contains [a list of things in the c_3].[end if]".
The cubicle part 1 is some text that varies. The cubicle part 1 is "[if c_3 is open and the c_3 contains nothing] The toolbox is empty! This is the worst thing that could possibly happen, ever![end if]".
The cubicle part 2 is some text that varies. The cubicle part 2 is "

You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_17 is "[cubicle part 0][cubicle part 1][cubicle part 2]".

The r_16 is mapped west of r_17.
Understand "workshop" as r_16.
The internal name of r_16 is "workshop".
The printed name of r_16 is "-= Workshop =-".
The workshop part 0 is some text that varies. The workshop part 0 is "You've entered a workshop.

 You hear a noise behind you and spin around, but you can't see anything other than a shelf. The shelf is ordinary.[if there is something on the s_5] On the shelf you make out [a list of things on the s_5].[end if]".
The workshop part 1 is some text that varies. The workshop part 1 is "[if there is nothing on the s_5] The shelf appears to be empty.[end if]".
The workshop part 2 is some text that varies. The workshop part 2 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The workshop part 3 is some text that varies. The workshop part 3 is " passageway leading north. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The workshop part 4 is some text that varies. The workshop part 4 is " portal leading south. You don't like doors? Why not try going east, that entranceway is unblocked.".
The description of r_16 is "[workshop part 0][workshop part 1][workshop part 2][workshop part 3][workshop part 4]".

south of r_16 and north of r_15 is a door called d_1.
north of r_16 and south of r_18 is a door called d_0.
The r_17 is mapped east of r_16.
Understand "canteen" as r_19.
The internal name of r_19 is "canteen".
The printed name of r_19 is "-= Canteen =-".
The canteen part 0 is some text that varies. The canteen part 0 is "Well, here we are in the canteen. You can barely contain your excitement.

 You can make out a Canadian limited edition box.[if c_4 is open and there is something in the c_4] The Canadian limited edition box contains [a list of things in the c_4].[end if]".
The canteen part 1 is some text that varies. The canteen part 1 is "[if c_4 is open and the c_4 contains nothing] What a letdown! The Canadian limited edition box is empty![end if]".
The canteen part 2 is some text that varies. The canteen part 2 is " You see a bowl. [if there is something on the s_6]On the bowl you can see [a list of things on the s_6].[end if]".
The canteen part 3 is some text that varies. The canteen part 3 is "[if there is nothing on the s_6]The bowl appears to be empty.[end if]".
The canteen part 4 is some text that varies. The canteen part 4 is "

You don't like doors? Why not try going west, that entranceway is unblocked.".
The description of r_19 is "[canteen part 0][canteen part 1][canteen part 2][canteen part 3][canteen part 4]".

The r_18 is mapped west of r_19.
Understand "closet" as r_18.
The internal name of r_18 is "closet".
The printed name of r_18 is "-= Closet =-".
The closet part 0 is some text that varies. The closet part 0 is "You find yourself in a closet.

 You bend down to tie your shoe. When you stand up, you notice a crate.[if c_5 is open and there is something in the c_5] The crate contains [a list of things in the c_5].[end if]".
The closet part 1 is some text that varies. The closet part 1 is "[if c_5 is open and the c_5 contains nothing] The crate is empty, what a horrible day![end if]".
The closet part 2 is some text that varies. The closet part 2 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The closet part 3 is some text that varies. The closet part 3 is " passageway leading south. There is an exit to the east. Don't worry, it is unguarded.".
The description of r_18 is "[closet part 0][closet part 1][closet part 2][closet part 3]".

south of r_18 and north of r_16 is a door called d_0.
The r_19 is mapped east of r_18.
Understand "study" as r_4.
The internal name of r_4 is "study".
The printed name of r_4 is "-= Study =-".
The study part 0 is some text that varies. The study part 0 is "I am obligated to announce that you are now in the study. You decide to just list off a complete list of everything you see in the room, because hey, why not?

 Look out! It's a- oh, never mind, it's just an armchair. The armchair is usual.[if there is something on the s_7] On the armchair you see [a list of things on the s_7]. I mean, just wow! Isn't TextWorld just the best?[end if]".
The study part 1 is some text that varies. The study part 1 is "[if there is nothing on the s_7] However, the armchair, like an empty armchair, has nothing on it. Hopefully this doesn't make you too upset.[end if]".
The study part 2 is some text that varies. The study part 2 is "

There is an exit to the east. Don't worry, it is unblocked. There is an unblocked exit to the south. There is an unblocked exit to the west.".
The description of r_4 is "[study part 0][study part 1][study part 2]".

The r_2 is mapped west of r_4.
The r_5 is mapped south of r_4.
The r_6 is mapped east of r_4.
Understand "parlor" as r_2.
The internal name of r_2 is "parlor".
The printed name of r_2 is "-= Parlor =-".
The parlor part 0 is some text that varies. The parlor part 0 is "You've just shown up in a parlor. You can barely contain your excitement.

 Oh, great. Here's a box. You wonder idly who left that here.[if c_6 is open and there is something in the c_6] The box contains [a list of things in the c_6]. You idly wonder how they came up with the name TextWorld for this place. It's pretty fitting.[end if]".
The parlor part 1 is some text that varies. The parlor part 1 is "[if c_6 is open and the c_6 contains nothing] What a letdown! The box is empty![end if]".
The parlor part 2 is some text that varies. The parlor part 2 is "

There is an exit to the east. Don't worry, it is unblocked. You don't like doors? Why not try going north, that entranceway is unblocked. There is an unblocked exit to the south.".
The description of r_2 is "[parlor part 0][parlor part 1][parlor part 2]".

The r_1 is mapped south of r_2.
The r_3 is mapped north of r_2.
The r_4 is mapped east of r_2.
Understand "laundry place" as r_5.
The internal name of r_5 is "laundry place".
The printed name of r_5 is "-= Laundry Place =-".
The laundry place part 0 is some text that varies. The laundry place part 0 is "You've entered a laundry place.

 What's that over there? It looks like it's a dresser.[if c_7 is open and there is something in the c_7] The dresser contains [a list of things in the c_7].[end if]".
The laundry place part 1 is some text that varies. The laundry place part 1 is "[if c_7 is open and the c_7 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The laundry place part 2 is some text that varies. The laundry place part 2 is " You can make out a table. Make a note of this, you might have to put stuff on or in it later on. The table is ordinary.[if there is something on the s_8] On the table you can make out [a list of things on the s_8].[end if]".
The laundry place part 3 is some text that varies. The laundry place part 3 is "[if there is nothing on the s_8] But the thing is empty.[end if]".
The laundry place part 4 is some text that varies. The laundry place part 4 is "

You don't like doors? Why not try going north, that entranceway is unguarded. There is an unblocked exit to the west.".
The description of r_5 is "[laundry place part 0][laundry place part 1][laundry place part 2][laundry place part 3][laundry place part 4]".

The r_1 is mapped west of r_5.
The r_4 is mapped north of r_5.
Understand "steam room" as r_1.
The internal name of r_1 is "steam room".
The printed name of r_1 is "-= Steam Room =-".
The steam room part 0 is some text that varies. The steam room part 0 is "You've just sauntered into a steam room. Okay, just remember what you're here to do, and everything will go great.

 You can see a bench! [if there is something on the s_9]On the bench you make out [a list of things on the s_9].[end if]".
The steam room part 1 is some text that varies. The steam room part 1 is "[if there is nothing on the s_9]But the thing is empty.[end if]".
The steam room part 2 is some text that varies. The steam room part 2 is "

There is an unblocked exit to the east. There is an exit to the north. Don't worry, it is unblocked. There is an exit to the south. Don't worry, it is unguarded.".
The description of r_1 is "[steam room part 0][steam room part 1][steam room part 2]".

The r_0 is mapped south of r_1.
The r_2 is mapped north of r_1.
The r_5 is mapped east of r_1.
Understand "silent workshop" as r_6.
The internal name of r_6 is "silent workshop".
The printed name of r_6 is "-= Silent Workshop =-".
The silent workshop part 0 is some text that varies. The silent workshop part 0 is "A well framed notice tells you that you are now in the silent workshop. You begin looking for stuff.

 You see a bookshelf. Wow, isn't TextWorld just the best? [if there is something on the s_10]You see [a list of things on the s_10] on the bookshelf. You idly wonder how they came up with the name TextWorld for this place. It's pretty fitting.[end if]".
The silent workshop part 1 is some text that varies. The silent workshop part 1 is "[if there is nothing on the s_10]But oh no! there's nothing on this piece of trash.[end if]".
The silent workshop part 2 is some text that varies. The silent workshop part 2 is "

There is an exit to the south. Don't worry, it is unblocked. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_6 is "[silent workshop part 0][silent workshop part 1][silent workshop part 2]".

The r_4 is mapped west of r_6.
The r_7 is mapped south of r_6.
Understand "basement" as r_8.
The internal name of r_8 is "basement".
The printed name of r_8 is "-= Basement =-".
The basement part 0 is some text that varies. The basement part 0 is "You arrive in a basement. An usual kind of place.

 You can make out a chest.[if c_8 is open and there is something in the c_8] The chest contains [a list of things in the c_8].[end if]".
The basement part 1 is some text that varies. The basement part 1 is "[if c_8 is open and the c_8 contains nothing] What a letdown! The chest is empty![end if]".
The basement part 2 is some text that varies. The basement part 2 is "

You don't like doors? Why not try going north, that entranceway is unblocked. You don't like doors? Why not try going south, that entranceway is unblocked. There is an exit to the west. Don't worry, it is unblocked.".
The description of r_8 is "[basement part 0][basement part 1][basement part 2]".

The r_10 is mapped west of r_8.
The r_9 is mapped south of r_8.
The r_7 is mapped north of r_8.
Understand "still cubicle" as r_11.
The internal name of r_11 is "still cubicle".
The printed name of r_11 is "-= Still Cubicle =-".
The still cubicle part 0 is some text that varies. The still cubicle part 0 is "You find yourself in a cubicle. A still one.



You don't like doors? Why not try going east, that entranceway is unguarded. You need an unguarded exit? You should try going north.".
The description of r_11 is "[still cubicle part 0]".

The r_10 is mapped north of r_11.
The r_9 is mapped east of r_11.
Understand "cellar" as r_3.
The internal name of r_3 is "cellar".
The printed name of r_3 is "-= Cellar =-".
The cellar part 0 is some text that varies. The cellar part 0 is "You've entered a cellar.



You don't like doors? Why not try going south, that entranceway is unblocked.".
The description of r_3 is "[cellar part 0]".

The r_2 is mapped south of r_3.
Understand "dish-pit" as r_7.
The internal name of r_7 is "dish-pit".
The printed name of r_7 is "-= Dish-Pit =-".
The dish-pit part 0 is some text that varies. The dish-pit part 0 is "Well, here we are in a dish-pit.



You need an unblocked exit? You should try going north. You need an unguarded exit? You should try going south.".
The description of r_7 is "[dish-pit part 0]".

The r_8 is mapped south of r_7.
The r_6 is mapped north of r_7.

The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 are containers.
The c_0 and the c_1 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 are privately-named.
The d_2 and the d_3 and the d_1 and the d_0 are doors.
The d_2 and the d_3 and the d_1 and the d_0 are privately-named.
The f_0 and the f_1 are foods.
The f_0 and the f_1 are privately-named.
The k_1 and the k_0 are keys.
The k_1 and the k_0 are privately-named.
The r_10 and the r_0 and the r_12 and the r_9 and the r_13 and the r_14 and the r_15 and the r_17 and the r_16 and the r_19 and the r_18 and the r_4 and the r_2 and the r_5 and the r_1 and the r_6 and the r_8 and the r_11 and the r_3 and the r_7 are rooms.
The r_10 and the r_0 and the r_12 and the r_9 and the r_13 and the r_14 and the r_15 and the r_17 and the r_16 and the r_19 and the r_18 and the r_4 and the r_2 and the r_5 and the r_1 and the r_6 and the r_8 and the r_11 and the r_3 and the r_7 are privately-named.
The s_0 and the s_1 and the s_10 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are supporters.
The s_0 and the s_1 and the s_10 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are privately-named.

The description of d_2 is "it is what it is, a gate [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_2 is "gate".
Understand "gate" as d_2.
The d_2 is open.
The description of d_3 is "The gateway looks solid. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_3 is "gateway".
Understand "gateway" as d_3.
The d_3 is open.
The description of d_1 is "it is what it is, a portal [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_1 is "portal".
Understand "portal" as d_1.
The d_1 is closed.
The description of d_0 is "The passageway looks towering. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_0 is "passageway".
Understand "passageway" as d_0.
The d_0 is locked.
The description of c_0 is "The portmanteau looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_0 is "portmanteau".
Understand "portmanteau" as c_0.
The c_0 is in r_9.
The c_0 is locked.
The description of c_1 is "The coffer looks strong, and impossible to break. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_1 is "coffer".
Understand "coffer" as c_1.
The c_1 is in r_13.
The c_1 is locked.
The description of c_2 is "The bureau looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_2 is "bureau".
Understand "bureau" as c_2.
The c_2 is in r_14.
The c_2 is closed.
The description of c_3 is "The toolbox looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "toolbox".
Understand "toolbox" as c_3.
The c_3 is in r_17.
The c_3 is locked.
The description of c_4 is "The Canadian limited edition box looks strong, and impossible to break. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_4 is "Canadian limited edition box".
Understand "Canadian limited edition box" as c_4.
Understand "Canadian" as c_4.
Understand "limited" as c_4.
Understand "edition" as c_4.
Understand "box" as c_4.
The c_4 is in r_19.
The c_4 is locked.
The description of c_5 is "The crate looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_5 is "crate".
Understand "crate" as c_5.
The c_5 is in r_18.
The c_5 is locked.
The description of c_6 is "The box looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_6 is "box".
Understand "box" as c_6.
The c_6 is in r_2.
The c_6 is closed.
The description of c_7 is "The dresser looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_7 is "dresser".
Understand "dresser" as c_7.
The c_7 is in r_5.
The c_7 is open.
The description of c_8 is "The chest looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_8 is "chest".
Understand "chest" as c_8.
The c_8 is in r_8.
The c_8 is open.
The description of f_0 is "You couldn't pay me to eat that standard thing.".
The printed name of f_0 is "gummy bear".
Understand "gummy bear" as f_0.
Understand "gummy" as f_0.
Understand "bear" as f_0.
The f_0 is in r_14.
The description of k_1 is "The metal of the Canadian limited edition latchkey is antiqued.".
The printed name of k_1 is "Canadian limited edition latchkey".
Understand "Canadian limited edition latchkey" as k_1.
Understand "Canadian" as k_1.
Understand "limited" as k_1.
Understand "edition" as k_1.
Understand "latchkey" as k_1.
The k_1 is in r_18.
The matching key of the c_4 is the k_1.
The description of s_0 is "The couch is wobbly.".
The printed name of s_0 is "couch".
Understand "couch" as s_0.
The s_0 is in r_10.
The description of s_1 is "The stand is reliable.".
The printed name of s_1 is "stand".
Understand "stand" as s_1.
The s_1 is in r_0.
The description of s_10 is "The bookshelf is shaky.".
The printed name of s_10 is "bookshelf".
Understand "bookshelf" as s_10.
The s_10 is in r_6.
The description of s_2 is "The rack is balanced.".
The printed name of s_2 is "rack".
Understand "rack" as s_2.
The s_2 is in r_12.
The description of s_3 is "The counter is solidly built.".
The printed name of s_3 is "counter".
Understand "counter" as s_3.
The s_3 is in r_13.
The description of s_4 is "The chair is solidly built.".
The printed name of s_4 is "chair".
Understand "chair" as s_4.
The s_4 is in r_15.
The description of s_5 is "The shelf is undependable.".
The printed name of s_5 is "shelf".
Understand "shelf" as s_5.
The s_5 is in r_16.
The description of s_6 is "The bowl is solidly built.".
The printed name of s_6 is "bowl".
Understand "bowl" as s_6.
The s_6 is in r_19.
The description of s_7 is "The armchair is solidly built.".
The printed name of s_7 is "armchair".
Understand "armchair" as s_7.
The s_7 is in r_4.
The description of s_8 is "The table is solidly built.".
The printed name of s_8 is "table".
Understand "table" as s_8.
The s_8 is in r_5.
The description of s_9 is "The bench is balanced.".
The printed name of s_9 is "bench".
Understand "bench" as s_9.
The s_9 is in r_1.
The description of k_0 is "The key is light.".
The printed name of k_0 is "key".
Understand "key" as k_0.
The k_0 is in the c_4.
The matching key of the d_0 is the k_0.
The description of f_1 is "You couldn't pay me to eat that typical thing.".
The printed name of f_1 is "stick of butter".
Understand "stick of butter" as f_1.
Understand "stick" as f_1.
Understand "butter" as f_1.
The f_1 is on the s_4.


The player is in r_19.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.

Test quest0_0 with "go west / take Canadian limited edition latchkey / go east / unlock Canadian limited edition box with Canadian limited edition latchkey / open Canadian limited edition box / take key from Canadian limited edition box / go west / unlock passageway with key / open passageway / go south / open portal / go south / go east / take gummy bear"

Every turn:
	if quest0 completed is true:
		do nothing;
	else if The player carries the f_1:
		end the story; [Lost]
	else if The player is in r_14 and The player carries the f_0:
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

The objective part 0 is some text that varies. The objective part 0 is "Who's got a virtual machine and is about to play through an fast paced round of TextWorld? You do! Here is your task for today. Your first objective is to make an effort to head west. After that, reco".
The objective part 1 is some text that varies. The objective part 1 is "ver the Canadian limited edition latchkey from the floor of the closet. Then, venture east. That done, unlock the Canadian limited edition box. And then, open the Canadian limited edition box within t".
The objective part 2 is some text that varies. The objective part 2 is "he canteen. And then, pick up the key from the Canadian limited edition box. And then, attempt to go to the west. After that, unlock the passageway within the closet with the key. And then, make it so".
The objective part 3 is some text that varies. The objective part 3 is " that the passageway inside the closet is open. Then, travel south. Okay, and then, open the portal. Having pulled open the portal, make an attempt to venture south. Then, venture east. Then, recover ".
The objective part 4 is some text that varies. The objective part 4 is "the gummy bear from the floor of the office. And if you do that, you're the winner!".

An objective is some text that varies. The objective is "[objective part 0][objective part 1][objective part 2][objective part 3][objective part 4]".
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

