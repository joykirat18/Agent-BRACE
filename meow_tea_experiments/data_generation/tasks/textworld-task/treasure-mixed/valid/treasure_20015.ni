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


The r_10 and the r_9 and the r_11 and the r_0 and the r_14 and the r_13 and the r_15 and the r_12 and the r_16 and the r_17 and the r_18 and the r_3 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_7 and the r_1 and the r_19 are rooms.

Understand "kitchen" as r_10.
The internal name of r_10 is "kitchen".
The printed name of r_10 is "-= Kitchen =-".
The kitchen part 0 is some text that varies. The kitchen part 0 is "You're now in the kitchen. Let's see what's in here.

 As if things weren't amazing enough already, you can even see a cabinet.[if c_0 is open and there is something in the c_0] The cabinet contains [a list of things in the c_0]![end if]".
The kitchen part 1 is some text that varies. The kitchen part 1 is "[if c_0 is open and the c_0 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The kitchen part 2 is some text that varies. The kitchen part 2 is "

There is an exit to the west. Don't worry, it is unblocked.".
The description of r_10 is "[kitchen part 0][kitchen part 1][kitchen part 2]".

The r_9 is mapped west of r_10.
Understand "shower" as r_9.
The internal name of r_9 is "shower".
The printed name of r_9 is "-= Shower =-".
The shower part 0 is some text that varies. The shower part 0 is "You arrive in a shower.

 You see a drawer.[if c_1 is open and there is something in the c_1] The drawer contains [a list of things in the c_1].[end if]".
The shower part 1 is some text that varies. The shower part 1 is "[if c_1 is open and the c_1 contains nothing] The drawer is empty! This is the worst thing that could possibly happen, ever![end if]".
The shower part 2 is some text that varies. The shower part 2 is " What's that over there? It looks like it's a dresser. Hmmm... what else, what else?[if c_2 is open and there is something in the c_2] The dresser contains [a list of things in the c_2]. Hmmm... what else, what else?[end if]".
The shower part 3 is some text that varies. The shower part 3 is "[if c_2 is open and the c_2 contains nothing] The dresser is empty! This is the worst thing that could possibly happen, ever![end if]".
The shower part 4 is some text that varies. The shower part 4 is " You make out [if c_3 is locked]a locked[else if c_3 is open]an opened[otherwise]a closed[end if]".
The shower part 5 is some text that varies. The shower part 5 is " box.[if c_3 is open and there is something in the c_3] The box contains [a list of things in the c_3].[end if]".
The shower part 6 is some text that varies. The shower part 6 is "[if c_3 is open and the c_3 contains nothing] What a letdown! The box is empty![end if]".
The shower part 7 is some text that varies. The shower part 7 is "

 There is [if d_3 is open]an open[otherwise]a closed[end if]".
The shower part 8 is some text that varies. The shower part 8 is " wooden portal leading north. There is [if d_4 is open]an open[otherwise]a closed[end if]".
The shower part 9 is some text that varies. The shower part 9 is " gate leading west. You need an unblocked exit? You should try going east.".
The description of r_9 is "[shower part 0][shower part 1][shower part 2][shower part 3][shower part 4][shower part 5][shower part 6][shower part 7][shower part 8][shower part 9]".

west of r_9 and east of r_1 is a door called d_4.
north of r_9 and south of r_3 is a door called d_3.
The r_10 is mapped east of r_9.
Understand "scullery" as r_11.
The internal name of r_11 is "scullery".
The printed name of r_11 is "-= Scullery =-".
The scullery part 0 is some text that varies. The scullery part 0 is "You arrive in a scullery. A typical one.

 If you haven't noticed it already, there seems to be something there by the wall, it's a counter. The counter is normal.[if there is something on the s_0] On the counter you can make out [a list of things on the s_0].[end if]".
The scullery part 1 is some text that varies. The scullery part 1 is "[if there is nothing on the s_0] However, the counter, like an empty counter, has nothing on it.[end if]".
The scullery part 2 is some text that varies. The scullery part 2 is "

There is an unblocked exit to the west.".
The description of r_11 is "[scullery part 0][scullery part 1][scullery part 2]".

The r_0 is mapped west of r_11.
Understand "canteen" as r_0.
The internal name of r_0 is "canteen".
The printed name of r_0 is "-= Canteen =-".
The canteen part 0 is some text that varies. The canteen part 0 is "You've entered a canteen.

 You scan the room, seeing a pan. The pan is standard.[if there is something on the s_1] On the pan you make out [a list of things on the s_1].[end if]".
The canteen part 1 is some text that varies. The canteen part 1 is "[if there is nothing on the s_1] But the thing hasn't got anything on it. What, you think everything in TextWorld should have stuff on it?[end if]".
The canteen part 2 is some text that varies. The canteen part 2 is "

 There is [if d_9 is open]an open[otherwise]a closed[end if]".
The canteen part 3 is some text that varies. The canteen part 3 is " Microsoft gate leading south. There is [if d_5 is open]an open[otherwise]a closed[end if]".
The canteen part 4 is some text that varies. The canteen part 4 is " passageway leading north. You need an unblocked exit? You should try going east.".
The description of r_0 is "[canteen part 0][canteen part 1][canteen part 2][canteen part 3][canteen part 4]".

south of r_0 and north of r_12 is a door called d_9.
north of r_0 and south of r_1 is a door called d_5.
The r_11 is mapped east of r_0.
Understand "lounge" as r_14.
The internal name of r_14 is "lounge".
The printed name of r_14 is "-= Lounge =-".
The lounge part 0 is some text that varies. The lounge part 0 is "You are in a lounge. An ordinary kind of place. Let's see what's in here.



 There is [if d_8 is open]an open[otherwise]a closed[end if]".
The lounge part 1 is some text that varies. The lounge part 1 is " hatch leading east. You don't like doors? Why not try going north, that entranceway is unguarded. You need an unguarded exit? You should try going west.".
The description of r_14 is "[lounge part 0][lounge part 1]".

The r_13 is mapped west of r_14.
The r_15 is mapped north of r_14.
east of r_14 and west of r_16 is a door called d_8.
Understand "basement" as r_13.
The internal name of r_13 is "basement".
The printed name of r_13 is "-= Basement =-".
The basement part 0 is some text that varies. The basement part 0 is "You are in a basement. An usual one. You can barely contain your excitement.

 You make out a display. Wow, isn't TextWorld just the best?[if c_4 is open and there is something in the c_4] The display contains [a list of things in the c_4]. Wow, isn't TextWorld just the best?[end if]".
The basement part 1 is some text that varies. The basement part 1 is "[if c_4 is open and the c_4 contains nothing] The display is empty, what a horrible day![end if]".
The basement part 2 is some text that varies. The basement part 2 is " You see [if c_5 is locked]a locked[else if c_5 is open]an opened[otherwise]a closed[end if]".
The basement part 3 is some text that varies. The basement part 3 is " case.[if c_5 is open and there is something in the c_5] The case contains [a list of things in the c_5].[end if]".
The basement part 4 is some text that varies. The basement part 4 is "[if c_5 is open and the c_5 contains nothing] The case is empty, what a horrible day![end if]".
The basement part 5 is some text that varies. The basement part 5 is "

There is an unblocked exit to the east. There is an unguarded exit to the north.".
The description of r_13 is "[basement part 0][basement part 1][basement part 2][basement part 3][basement part 4][basement part 5]".

The r_12 is mapped north of r_13.
The r_14 is mapped east of r_13.
Understand "spare room" as r_15.
The internal name of r_15 is "spare room".
The printed name of r_15 is "-= Spare Room =-".
The spare room part 0 is some text that varies. The spare room part 0 is "You have come into the most ordinary of all possible spare rooms. You decide to just list off a complete list of everything you see in the room, because hey, why not?

 [if c_6 is locked]A locked[else if c_6 is open]An open[otherwise]A closed[end if]".
The spare room part 1 is some text that varies. The spare room part 1 is " crate is nearby.[if c_6 is open and there is something in the c_6] The crate contains [a list of things in the c_6]. You wonder idly who left that here.[end if]".
The spare room part 2 is some text that varies. The spare room part 2 is "[if c_6 is open and the c_6 contains nothing] What a letdown! The crate is empty![end if]".
The spare room part 3 is some text that varies. The spare room part 3 is " You can see [if c_7 is locked]a locked[else if c_7 is open]an opened[otherwise]a closed[end if]".
The spare room part 4 is some text that varies. The spare room part 4 is " suitcase in the corner.[if c_7 is open and there is something in the c_7] The suitcase contains [a list of things in the c_7]. Classic TextWorld.[end if]".
The spare room part 5 is some text that varies. The spare room part 5 is "[if c_7 is open and the c_7 contains nothing] The suitcase is empty, what a horrible day![end if]".
The spare room part 6 is some text that varies. The spare room part 6 is "

There is an unguarded exit to the south. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_15 is "[spare room part 0][spare room part 1][spare room part 2][spare room part 3][spare room part 4][spare room part 5][spare room part 6]".

The r_12 is mapped west of r_15.
The r_14 is mapped south of r_15.
Understand "kitchenette" as r_12.
The internal name of r_12 is "kitchenette".
The printed name of r_12 is "-= Kitchenette =-".
The kitchenette part 0 is some text that varies. The kitchenette part 0 is "You find yourself in a kitchenette. A typical kind of place.



 There is [if d_9 is open]an open[otherwise]a closed[end if]".
The kitchenette part 1 is some text that varies. The kitchenette part 1 is " Microsoft gate leading north. There is an exit to the east. Don't worry, it is unguarded. You need an unblocked exit? You should try going south.".
The description of r_12 is "[kitchenette part 0][kitchenette part 1]".

The r_13 is mapped south of r_12.
north of r_12 and south of r_0 is a door called d_9.
The r_15 is mapped east of r_12.
Understand "sauna" as r_16.
The internal name of r_16 is "sauna".
The printed name of r_16 is "-= Sauna =-".
The sauna part 0 is some text that varies. The sauna part 0 is "Look at you, bigshot, walking into a sauna like it isn't some huge deal.

 You make out a trunk.[if c_8 is open and there is something in the c_8] The trunk contains [a list of things in the c_8]. Now that's what I call TextWorld![end if]".
The sauna part 1 is some text that varies. The sauna part 1 is "[if c_8 is open and the c_8 contains nothing] The trunk is empty, what a horrible day![end if]".
The sauna part 2 is some text that varies. The sauna part 2 is "

 There is [if d_7 is open]an open[otherwise]a closed[end if]".
The sauna part 3 is some text that varies. The sauna part 3 is " gateway leading east. There is [if d_8 is open]an open[otherwise]a closed[end if]".
The sauna part 4 is some text that varies. The sauna part 4 is " hatch leading west.".
The description of r_16 is "[sauna part 0][sauna part 1][sauna part 2][sauna part 3][sauna part 4]".

west of r_16 and east of r_14 is a door called d_8.
east of r_16 and west of r_17 is a door called d_7.
Understand "cookhouse" as r_17.
The internal name of r_17 is "cookhouse".
The printed name of r_17 is "-= Cookhouse =-".
The cookhouse part 0 is some text that varies. The cookhouse part 0 is "Ah, the cookhouse. This is some kind of cookhouse, really great standard vibes in this place, a wonderful standard atmosphere. I guess you better just go and list everything you see here.



 There is [if d_6 is open]an open[otherwise]a closed[end if]".
The cookhouse part 1 is some text that varies. The cookhouse part 1 is " door leading east. There is [if d_7 is open]an open[otherwise]a closed[end if]".
The cookhouse part 2 is some text that varies. The cookhouse part 2 is " gateway leading west.".
The description of r_17 is "[cookhouse part 0][cookhouse part 1][cookhouse part 2]".

west of r_17 and east of r_16 is a door called d_7.
east of r_17 and west of r_18 is a door called d_6.
Understand "workshop" as r_18.
The internal name of r_18 is "workshop".
The printed name of r_18 is "-= Workshop =-".
The workshop part 0 is some text that varies. The workshop part 0 is "You are in a workshop. An ordinary kind of place. You decide to just list off a complete list of everything you see in the room, because hey, why not?

 You can see an armchair. The armchair is typical.[if there is something on the s_2] On the armchair you can make out [a list of things on the s_2].[end if]".
The workshop part 1 is some text that varies. The workshop part 1 is "[if there is nothing on the s_2] Unfortunately, there isn't a thing on it. Hm. Oh well[end if]".
The workshop part 2 is some text that varies. The workshop part 2 is "

 There is [if d_6 is open]an open[otherwise]a closed[end if]".
The workshop part 3 is some text that varies. The workshop part 3 is " door leading west. You need an unblocked exit? You should try going north.".
The description of r_18 is "[workshop part 0][workshop part 1][workshop part 2][workshop part 3]".

west of r_18 and east of r_17 is a door called d_6.
The r_19 is mapped north of r_18.
Understand "dish-pit" as r_3.
The internal name of r_3 is "dish-pit".
The printed name of r_3 is "-= Dish-Pit =-".
The dish-pit part 0 is some text that varies. The dish-pit part 0 is "I am sorry to announce that you are now in the dish-pit.

 You make out [if c_9 is locked]a locked[else if c_9 is open]an opened[otherwise]a closed[end if]".
The dish-pit part 1 is some text that varies. The dish-pit part 1 is " refrigerator close by.[if c_9 is open and there is something in the c_9] The refrigerator contains [a list of things in the c_9].[end if]".
The dish-pit part 2 is some text that varies. The dish-pit part 2 is "[if c_9 is open and the c_9 contains nothing] What a letdown! The refrigerator is empty![end if]".
The dish-pit part 3 is some text that varies. The dish-pit part 3 is " You make out a bowl. [if there is something on the s_3]On the bowl you make out [a list of things on the s_3].[end if]".
The dish-pit part 4 is some text that varies. The dish-pit part 4 is "[if there is nothing on the s_3]But the thing is empty. It would have been so cool if there was stuff on the bowl.[end if]".
The dish-pit part 5 is some text that varies. The dish-pit part 5 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The dish-pit part 6 is some text that varies. The dish-pit part 6 is " portal leading east. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The dish-pit part 7 is some text that varies. The dish-pit part 7 is " wooden portal leading south. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_3 is "[dish-pit part 0][dish-pit part 1][dish-pit part 2][dish-pit part 3][dish-pit part 4][dish-pit part 5][dish-pit part 6][dish-pit part 7]".

The r_2 is mapped west of r_3.
south of r_3 and north of r_9 is a door called d_3.
east of r_3 and west of r_4 is a door called d_2.
Understand "cubicle" as r_2.
The internal name of r_2 is "cubicle".
The printed name of r_2 is "-= Cubicle =-".
The cubicle part 0 is some text that varies. The cubicle part 0 is "You've just shown up in a cubicle.



There is an unblocked exit to the east. There is an exit to the south. Don't worry, it is unblocked.".
The description of r_2 is "[cubicle part 0]".

The r_1 is mapped south of r_2.
The r_3 is mapped east of r_2.
Understand "steam room" as r_4.
The internal name of r_4 is "steam room".
The printed name of r_4 is "-= Steam Room =-".
The steam room part 0 is some text that varies. The steam room part 0 is "You've stumbled into an usual room. Your mind races to think of what kind of room would be usual. And then it hits you. Of course. You're in the steam room.



 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The steam room part 1 is some text that varies. The steam room part 1 is " fresh laundry scented hatch leading east. There is [if d_2 is open]an open[otherwise]a closed[end if]".
The steam room part 2 is some text that varies. The steam room part 2 is " portal leading west.".
The description of r_4 is "[steam room part 0][steam room part 1][steam room part 2]".

west of r_4 and east of r_3 is a door called d_2.
east of r_4 and west of r_5 is a door called d_1.
Understand "vault" as r_5.
The internal name of r_5 is "vault".
The printed name of r_5 is "-= Vault =-".
The vault part 0 is some text that varies. The vault part 0 is "You find yourself in a vault. An ordinary one. The room is well lit.



 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The vault part 1 is some text that varies. The vault part 1 is " spherical hatch leading south. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The vault part 2 is some text that varies. The vault part 2 is " fresh laundry scented hatch leading west. You don't like doors? Why not try going east, that entranceway is unguarded.".
The description of r_5 is "[vault part 0][vault part 1][vault part 2]".

west of r_5 and east of r_4 is a door called d_1.
south of r_5 and north of r_7 is a door called d_0.
The r_6 is mapped east of r_5.
Understand "cookery" as r_6.
The internal name of r_6 is "cookery".
The printed name of r_6 is "-= Cookery =-".
The cookery part 0 is some text that varies. The cookery part 0 is "You find yourself in a cookery. A typical one.

 Look over there! a platter. [if there is something on the s_4]You see [a list of things on the s_4] on the platter.[end if]".
The cookery part 1 is some text that varies. The cookery part 1 is "[if there is nothing on the s_4]But the thing hasn't got anything on it. It would have been so cool if there was stuff on the platter.[end if]".
The cookery part 2 is some text that varies. The cookery part 2 is " You can make out a shelf. [if there is something on the s_5]On the shelf you see [a list of things on the s_5].[end if]".
The cookery part 3 is some text that varies. The cookery part 3 is "[if there is nothing on the s_5]Looks like someone's already been here and taken everything off it, though.[end if]".
The cookery part 4 is some text that varies. The cookery part 4 is "

You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_6 is "[cookery part 0][cookery part 1][cookery part 2][cookery part 3][cookery part 4]".

The r_5 is mapped west of r_6.
Understand "parlor" as r_8.
The internal name of r_8 is "parlor".
The printed name of r_8 is "-= Parlor =-".
The parlor part 0 is some text that varies. The parlor part 0 is "You arrive in a parlor. An ordinary kind of place.

 You scan the room for a chest, and you find a chest.[if c_10 is open and there is something in the c_10] The chest contains [a list of things in the c_10].[end if]".
The parlor part 1 is some text that varies. The parlor part 1 is "[if c_10 is open and the c_10 contains nothing] The chest is empty! What a waste of a day![end if]".
The parlor part 2 is some text that varies. The parlor part 2 is " You see a desk. You wonder idly who left that here. [if there is something on the s_6]You see [a list of things on the s_6] on the desk.[end if]".
The parlor part 3 is some text that varies. The parlor part 3 is "[if there is nothing on the s_6]The desk appears to be empty. What, you think everything in TextWorld should have stuff on it?[end if]".
The parlor part 4 is some text that varies. The parlor part 4 is "

There is an exit to the west. Don't worry, it is unguarded.".
The description of r_8 is "[parlor part 0][parlor part 1][parlor part 2][parlor part 3][parlor part 4]".

The r_7 is mapped west of r_8.
Understand "study" as r_7.
The internal name of r_7 is "study".
The printed name of r_7 is "-= Study =-".
The study part 0 is some text that varies. The study part 0 is "You find yourself in a study. A normal one. Let's see what's in here.



 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The study part 1 is some text that varies. The study part 1 is " spherical hatch leading north. There is an exit to the east. Don't worry, it is unblocked.".
The description of r_7 is "[study part 0][study part 1]".

north of r_7 and south of r_5 is a door called d_0.
The r_8 is mapped east of r_7.
Understand "launderette" as r_1.
The internal name of r_1 is "launderette".
The printed name of r_1 is "-= Launderette =-".
The launderette part 0 is some text that varies. The launderette part 0 is "Well, here we are in the launderette. You begin looking for stuff.



 There is [if d_4 is open]an open[otherwise]a closed[end if]".
The launderette part 1 is some text that varies. The launderette part 1 is " gate leading east. There is [if d_5 is open]an open[otherwise]a closed[end if]".
The launderette part 2 is some text that varies. The launderette part 2 is " passageway leading south. You don't like doors? Why not try going north, that entranceway is unblocked.".
The description of r_1 is "[launderette part 0][launderette part 1][launderette part 2]".

south of r_1 and north of r_0 is a door called d_5.
The r_2 is mapped north of r_1.
east of r_1 and west of r_9 is a door called d_4.
Understand "bar" as r_19.
The internal name of r_19 is "bar".
The printed name of r_19 is "-= Bar =-".
The bar part 0 is some text that varies. The bar part 0 is "You've just shown up in a bar. I guess you better just go and list everything you see here.

 You can see a bed stand. [if there is something on the s_7]On the bed stand you can see [a list of things on the s_7].[end if]".
The bar part 1 is some text that varies. The bar part 1 is "[if there is nothing on the s_7]However, the bed stand, like an empty bed stand, has nothing on it. It would have been so cool if there was stuff on the bed stand.[end if]".
The bar part 2 is some text that varies. The bar part 2 is " You see a stand. [if there is something on the s_8]On the stand you can see [a list of things on the s_8].[end if]".
The bar part 3 is some text that varies. The bar part 3 is "[if there is nothing on the s_8]But the thing is empty. What, you think everything in TextWorld should have stuff on it?[end if]".
The bar part 4 is some text that varies. The bar part 4 is "

There is an exit to the south. Don't worry, it is unguarded.".
The description of r_19 is "[bar part 0][bar part 1][bar part 2][bar part 3][bar part 4]".

The r_18 is mapped south of r_19.

The c_0 and the c_1 and the c_10 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are containers.
The c_0 and the c_1 and the c_10 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are privately-named.
The d_5 and the d_9 and the d_4 and the d_8 and the d_7 and the d_6 and the d_2 and the d_3 and the d_1 and the d_0 are doors.
The d_5 and the d_9 and the d_4 and the d_8 and the d_7 and the d_6 and the d_2 and the d_3 and the d_1 and the d_0 are privately-named.
The k_0 and the k_1 and the k_3 and the k_2 and the k_4 are keys.
The k_0 and the k_1 and the k_3 and the k_2 and the k_4 are privately-named.
The o_0 are object-likes.
The o_0 are privately-named.
The r_10 and the r_9 and the r_11 and the r_0 and the r_14 and the r_13 and the r_15 and the r_12 and the r_16 and the r_17 and the r_18 and the r_3 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_7 and the r_1 and the r_19 are rooms.
The r_10 and the r_9 and the r_11 and the r_0 and the r_14 and the r_13 and the r_15 and the r_12 and the r_16 and the r_17 and the r_18 and the r_3 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_7 and the r_1 and the r_19 are privately-named.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 are supporters.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 are privately-named.

The description of d_5 is "The passageway looks noble. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_5 is "passageway".
Understand "passageway" as d_5.
The d_5 is open.
The description of d_9 is "it's an imposing Microsoft gate [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_9 is "Microsoft gate".
Understand "Microsoft gate" as d_9.
Understand "Microsoft" as d_9.
Understand "gate" as d_9.
The d_9 is locked.
The description of d_4 is "it's a solid gate [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_4 is "gate".
Understand "gate" as d_4.
The d_4 is open.
The description of d_8 is "it's a manageable hatch [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_8 is "hatch".
Understand "hatch" as d_8.
The d_8 is open.
The description of d_7 is "The gateway looks durable. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_7 is "gateway".
Understand "gateway" as d_7.
The d_7 is open.
The description of d_6 is "it is what it is, a door [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_6 is "door".
Understand "door" as d_6.
The d_6 is open.
The description of d_2 is "it is what it is, a portal [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_2 is "portal".
Understand "portal" as d_2.
The d_2 is locked.
The description of d_3 is "it's a noble portal [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_3 is "wooden portal".
Understand "wooden portal" as d_3.
Understand "wooden" as d_3.
Understand "portal" as d_3.
The d_3 is open.
The description of d_1 is "it is what it is, a fresh laundry scented hatch [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_1 is "fresh laundry scented hatch".
Understand "fresh laundry scented hatch" as d_1.
Understand "fresh" as d_1.
Understand "laundry" as d_1.
Understand "scented" as d_1.
Understand "hatch" as d_1.
The d_1 is locked.
The description of d_0 is "it's a solid spherical hatch [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_0 is "spherical hatch".
Understand "spherical hatch" as d_0.
Understand "spherical" as d_0.
Understand "hatch" as d_0.
The d_0 is locked.
The description of c_0 is "The cabinet looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_0 is "cabinet".
Understand "cabinet" as c_0.
The c_0 is in r_10.
The c_0 is open.
The description of c_1 is "The drawer looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_1 is "drawer".
Understand "drawer" as c_1.
The c_1 is in r_9.
The c_1 is open.
The description of c_10 is "The chest looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_10 is "chest".
Understand "chest" as c_10.
The c_10 is in r_8.
The c_10 is locked.
The description of c_2 is "The dresser looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_2 is "dresser".
Understand "dresser" as c_2.
The c_2 is in r_9.
The c_2 is closed.
The description of c_3 is "The box looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "box".
Understand "box" as c_3.
The c_3 is in r_9.
The c_3 is closed.
The description of c_4 is "The display looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_4 is "display".
Understand "display" as c_4.
The c_4 is in r_13.
The c_4 is closed.
The description of c_5 is "The case looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_5 is "case".
Understand "case" as c_5.
The c_5 is in r_13.
The c_5 is closed.
The description of c_6 is "The crate looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_6 is "crate".
Understand "crate" as c_6.
The c_6 is in r_15.
The c_6 is open.
The description of c_7 is "The suitcase looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_7 is "suitcase".
Understand "suitcase" as c_7.
The c_7 is in r_15.
The c_7 is closed.
The description of c_8 is "The trunk looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_8 is "trunk".
Understand "trunk" as c_8.
The c_8 is in r_16.
The c_8 is open.
The description of c_9 is "The refrigerator looks strong, and impossible to break. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_9 is "refrigerator".
Understand "refrigerator" as c_9.
The c_9 is in r_3.
The c_9 is open.
The description of k_0 is "The passkey is light.".
The printed name of k_0 is "passkey".
Understand "passkey" as k_0.
The k_0 is in r_4.
The description of k_1 is "The Microsoft latchkey is cold to the touch".
The printed name of k_1 is "Microsoft latchkey".
Understand "Microsoft latchkey" as k_1.
Understand "Microsoft" as k_1.
Understand "latchkey" as k_1.
The k_1 is in r_1.
The matching key of the d_9 is the k_1.
The description of k_3 is "The fresh laundry scented key looks useful".
The printed name of k_3 is "fresh laundry scented key".
Understand "fresh laundry scented key" as k_3.
Understand "fresh" as k_3.
Understand "laundry" as k_3.
Understand "scented" as k_3.
Understand "key" as k_3.
The k_3 is in r_7.
The matching key of the d_1 is the k_3.
The description of o_0 is "The ladle appears to be out of place here".
The printed name of o_0 is "ladle".
Understand "ladle" as o_0.
The o_0 is in r_12.
The description of s_0 is "The counter is an unstable piece of junk.".
The printed name of s_0 is "counter".
Understand "counter" as s_0.
The s_0 is in r_11.
The description of s_1 is "The pan is solid.".
The printed name of s_1 is "pan".
Understand "pan" as s_1.
The s_1 is in r_0.
The description of s_2 is "The armchair is solidly built.".
The printed name of s_2 is "armchair".
Understand "armchair" as s_2.
The s_2 is in r_18.
The description of s_3 is "The bowl is undependable.".
The printed name of s_3 is "bowl".
Understand "bowl" as s_3.
The s_3 is in r_3.
The description of s_4 is "The platter is durable.".
The printed name of s_4 is "platter".
Understand "platter" as s_4.
The s_4 is in r_6.
The description of s_5 is "The shelf is durable.".
The printed name of s_5 is "shelf".
Understand "shelf" as s_5.
The s_5 is in r_6.
The description of s_6 is "The desk is solid.".
The printed name of s_6 is "desk".
Understand "desk" as s_6.
The s_6 is in r_8.
The description of s_7 is "The bed stand is solid.".
The printed name of s_7 is "bed stand".
Understand "bed stand" as s_7.
Understand "bed" as s_7.
Understand "stand" as s_7.
The s_7 is in r_19.
The description of s_8 is "The stand is reliable.".
The printed name of s_8 is "stand".
Understand "stand" as s_8.
The s_8 is in r_19.
The description of k_2 is "The latchkey is cold to the touch".
The printed name of k_2 is "latchkey".
Understand "latchkey" as k_2.
The player carries the k_2.
The matching key of the d_2 is the k_2.
The description of k_4 is "The spherical passkey is cold to the touch".
The printed name of k_4 is "spherical passkey".
Understand "spherical passkey" as k_4.
Understand "spherical" as k_4.
Understand "passkey" as k_4.
The player carries the k_4.
The matching key of the d_0 is the k_4.


The player is in r_6.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.

Test quest0_0 with "go west / unlock spherical hatch with spherical passkey / open spherical hatch / go south / take fresh laundry scented key / go north / unlock fresh laundry scented hatch with fresh laundry scented key / open fresh laundry scented hatch / go west / unlock portal with latchkey / open portal / go west / go west / go south / take Microsoft latchkey / go south / unlock Microsoft gate with Microsoft latchkey / open Microsoft gate / go south / take ladle"

Every turn:
	if quest0 completed is true:
		do nothing;
	else if The player carries the k_0:
		end the story; [Lost]
	else if The player is in r_12 and The player carries the o_0:
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

The objective part 0 is some text that varies. The objective part 0 is "You are now playing a profound session of TextWorld! First off, if it's not too much trouble, I need you to venture west. That done, check that the spherical hatch is unlocked with the spherical passk".
The objective part 1 is some text that varies. The objective part 1 is "ey. After unlocking the spherical hatch, ensure that the spherical hatch within the vault is open. After opening the spherical hatch, take a trip south. With that over with, recover the fresh laundry ".
The objective part 2 is some text that varies. The objective part 2 is "scented key from the floor of the study. Having got the fresh laundry scented key, travel north. Then, unlock the fresh laundry scented hatch in the vault. After that, open the fresh laundry scented h".
The objective part 3 is some text that varies. The objective part 3 is "atch. And then, try to travel west. With that accomplished, unlock the portal. After that, open the portal in the steam room. After that, attempt to move west. If you can manage that, attempt to trave".
The objective part 4 is some text that varies. The objective part 4 is "l west. With that done, travel south. Following that, lift the Microsoft latchkey from the floor of the launderette. And then, head south. Then, insert the Microsoft latchkey into the Microsoft gate w".
The objective part 5 is some text that varies. The objective part 5 is "ithin the canteen's lock to unlock it. After unlocking the Microsoft gate, make sure that the Microsoft gate is ajar. And then, move south. With that accomplished, lift the ladle from the floor of the".
The objective part 6 is some text that varies. The objective part 6 is " kitchenette. And once you've done that, you win!".

An objective is some text that varies. The objective is "[objective part 0][objective part 1][objective part 2][objective part 3][objective part 4][objective part 5][objective part 6]".
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

