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


The r_1 and the r_0 and the r_10 and the r_9 and the r_11 and the r_3 and the r_13 and the r_12 and the r_14 and the r_19 and the r_15 and the r_16 and the r_17 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_18 and the r_7 are rooms.

Understand "vault" as r_1.
The internal name of r_1 is "vault".
The printed name of r_1 is "-= Vault =-".
The vault part 0 is some text that varies. The vault part 0 is "You find yourself in a vault. An ordinary one.

 What's that over there? It looks like it's a crate.[if c_0 is open and there is something in the c_0] The crate contains [a list of things in the c_0].[end if]".
The vault part 1 is some text that varies. The vault part 1 is "[if c_0 is open and the c_0 contains nothing] The crate is empty, what a horrible day![end if]".
The vault part 2 is some text that varies. The vault part 2 is "

There is an exit to the east. Don't worry, it is unguarded. You need an unblocked exit? You should try going north. There is an unguarded exit to the west.".
The description of r_1 is "[vault part 0][vault part 1][vault part 2]".

The r_0 is mapped west of r_1.
The r_2 is mapped north of r_1.
The r_4 is mapped east of r_1.
Understand "cookhouse" as r_0.
The internal name of r_0 is "cookhouse".
The printed name of r_0 is "-= Cookhouse =-".
The cookhouse part 0 is some text that varies. The cookhouse part 0 is "Well, here we are in a cookhouse.



There is an unblocked exit to the east. You need an unblocked exit? You should try going north.".
The description of r_0 is "[cookhouse part 0]".

The r_7 is mapped north of r_0.
The r_1 is mapped east of r_0.
Understand "pantry" as r_10.
The internal name of r_10 is "pantry".
The printed name of r_10 is "-= Pantry =-".
The pantry part 0 is some text that varies. The pantry part 0 is "You arrive in a pantry. An usual kind of place. You begin to take stock of what's in the room.

 You make out [if c_1 is locked]a locked[else if c_1 is open]an opened[otherwise]a closed[end if]".
The pantry part 1 is some text that varies. The pantry part 1 is " safe right there by you.[if c_1 is open and there is something in the c_1] The safe contains [a list of things in the c_1].[end if]".
The pantry part 2 is some text that varies. The pantry part 2 is "[if c_1 is open and the c_1 contains nothing] What a letdown! The safe is empty![end if]".
The pantry part 3 is some text that varies. The pantry part 3 is "

There is an exit to the east. Don't worry, it is unblocked. You don't like doors? Why not try going north, that entranceway is unblocked. There is an exit to the south. Don't worry, it is unblocked. There is an unblocked exit to the west.".
The description of r_10 is "[pantry part 0][pantry part 1][pantry part 2][pantry part 3]".

The r_9 is mapped west of r_10.
The r_3 is mapped south of r_10.
The r_12 is mapped north of r_10.
The r_16 is mapped east of r_10.
Understand "lounge" as r_9.
The internal name of r_9 is "lounge".
The printed name of r_9 is "-= Lounge =-".
The lounge part 0 is some text that varies. The lounge part 0 is "Of every lounge you could have walked into, you had to saunter into a typical one. You begin looking for stuff.

 You make out [if c_2 is locked]a locked[else if c_2 is open]an opened[otherwise]a closed[end if]".
The lounge part 1 is some text that varies. The lounge part 1 is " portmanteau.[if c_2 is open and there is something in the c_2] The portmanteau contains [a list of things in the c_2]. You check the price tag that the portmanteau's owner still hasn't taken off. Two hundred bucks?! That's ridiculous! You ever meet my good friend, they work for the mayor? I'm sure my friend could get you one of those for 45 bucks![end if]".
The lounge part 2 is some text that varies. The lounge part 2 is "[if c_2 is open and the c_2 contains nothing] The portmanteau is empty, what a horrible day![end if]".
The lounge part 3 is some text that varies. The lounge part 3 is "

You don't like doors? Why not try going east, that entranceway is unblocked. There is an exit to the south. Don't worry, it is unguarded. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_9 is "[lounge part 0][lounge part 1][lounge part 2][lounge part 3]".

The r_8 is mapped west of r_9.
The r_2 is mapped south of r_9.
The r_10 is mapped east of r_9.
Understand "spare room" as r_11.
The internal name of r_11 is "spare room".
The printed name of r_11 is "-= Spare Room =-".
The spare room part 0 is some text that varies. The spare room part 0 is "You arrive in a spare room. A normal kind of place. You begin looking for stuff.



You need an unguarded exit? You should try going north. You need an unblocked exit? You should try going south. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_11 is "[spare room part 0]".

The r_3 is mapped west of r_11.
The r_5 is mapped south of r_11.
The r_16 is mapped north of r_11.
Understand "scullery" as r_3.
The internal name of r_3 is "scullery".
The printed name of r_3 is "-= Scullery =-".
The scullery part 0 is some text that varies. The scullery part 0 is "You are in a scullery. A normal kind of place.

 You see a gleam over in a corner, where you can see a fridge.[if c_3 is open and there is something in the c_3] The fridge contains [a list of things in the c_3].[end if]".
The scullery part 1 is some text that varies. The scullery part 1 is "[if c_3 is open and the c_3 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The scullery part 2 is some text that varies. The scullery part 2 is "

You need an unblocked exit? You should try going east. You need an unguarded exit? You should try going north. You don't like doors? Why not try going south, that entranceway is unblocked. There is an unblocked exit to the west.".
The description of r_3 is "[scullery part 0][scullery part 1][scullery part 2]".

The r_2 is mapped west of r_3.
The r_4 is mapped south of r_3.
The r_10 is mapped north of r_3.
The r_11 is mapped east of r_3.
Understand "chamber" as r_13.
The internal name of r_13 is "chamber".
The printed name of r_13 is "-= Chamber =-".
The chamber part 0 is some text that varies. The chamber part 0 is "Well how about that, you are in a place we're calling a chamber.

 You rest your hand against a wall, but you miss the wall and fall onto a box.[if c_4 is open and there is something in the c_4] The box contains [a list of things in the c_4].[end if]".
The chamber part 1 is some text that varies. The chamber part 1 is "[if c_4 is open and the c_4 contains nothing] What a letdown! The box is empty![end if]".
The chamber part 2 is some text that varies. The chamber part 2 is " You can make out [if c_5 is locked]a locked[else if c_5 is open]an opened[otherwise]a closed[end if]".
The chamber part 3 is some text that varies. The chamber part 3 is " coffer.[if c_5 is open and there is something in the c_5] The coffer contains [a list of things in the c_5]. Huh, weird.[end if]".
The chamber part 4 is some text that varies. The chamber part 4 is "[if c_5 is open and the c_5 contains nothing] What a letdown! The coffer is empty![end if]".
The chamber part 5 is some text that varies. The chamber part 5 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The chamber part 6 is some text that varies. The chamber part 6 is " passageway leading east. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The chamber part 7 is some text that varies. The chamber part 7 is " portal leading north. You need an unguarded exit? You should try going south. There is an exit to the west. Don't worry, it is unblocked.".
The description of r_13 is "[chamber part 0][chamber part 1][chamber part 2][chamber part 3][chamber part 4][chamber part 5][chamber part 6][chamber part 7]".

The r_12 is mapped west of r_13.
The r_16 is mapped south of r_13.
north of r_13 and south of r_14 is a door called d_1.
east of r_13 and west of r_17 is a door called d_0.
Understand "washroom" as r_12.
The internal name of r_12 is "washroom".
The printed name of r_12 is "-= Washroom =-".
The washroom part 0 is some text that varies. The washroom part 0 is "You are in a washroom. A normal one. You can barely contain your excitement.

 You can see [if c_6 is locked]a locked[else if c_6 is open]an opened[otherwise]a closed[end if]".
The washroom part 1 is some text that varies. The washroom part 1 is " basket.[if c_6 is open and there is something in the c_6] The basket contains [a list of things in the c_6].[end if]".
The washroom part 2 is some text that varies. The washroom part 2 is "[if c_6 is open and the c_6 contains nothing] The basket is empty! This is the worst thing that could possibly happen, ever![end if]".
The washroom part 3 is some text that varies. The washroom part 3 is " If you haven't noticed it already, there seems to be something there by the wall, it's a cabinet.[if c_7 is open and there is something in the c_7] The cabinet contains [a list of things in the c_7].[end if]".
The washroom part 4 is some text that varies. The washroom part 4 is "[if c_7 is open and the c_7 contains nothing] What a letdown! The cabinet is empty![end if]".
The washroom part 5 is some text that varies. The washroom part 5 is "

There is an unblocked exit to the east. You need an unblocked exit? You should try going south.".
The description of r_12 is "[washroom part 0][washroom part 1][washroom part 2][washroom part 3][washroom part 4][washroom part 5]".

The r_10 is mapped south of r_12.
The r_13 is mapped east of r_12.
Understand "attic" as r_14.
The internal name of r_14 is "attic".
The printed name of r_14 is "-= Attic =-".
The attic part 0 is some text that varies. The attic part 0 is "You are in an attic. A typical kind of place.

 You make out a counter. [if there is something on the s_0]On the counter you can see [a list of things on the s_0].[end if]".
The attic part 1 is some text that varies. The attic part 1 is "[if there is nothing on the s_0]But the thing hasn't got anything on it. Oh! Why couldn't there just be stuff on it?[end if]".
The attic part 2 is some text that varies. The attic part 2 is " You make out a shelf. The shelf is standard.[if there is something on the s_1] On the shelf you can make out [a list of things on the s_1].[end if]".
The attic part 3 is some text that varies. The attic part 3 is "[if there is nothing on the s_1] But oh no! there's nothing on this piece of junk.[end if]".
The attic part 4 is some text that varies. The attic part 4 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The attic part 5 is some text that varies. The attic part 5 is " portal leading south. There is an unblocked exit to the east. There is an unblocked exit to the west.".
The description of r_14 is "[attic part 0][attic part 1][attic part 2][attic part 3][attic part 4][attic part 5]".

The r_19 is mapped west of r_14.
south of r_14 and north of r_13 is a door called d_1.
The r_15 is mapped east of r_14.
Understand "basement" as r_19.
The internal name of r_19 is "basement".
The printed name of r_19 is "-= Basement =-".
The basement part 0 is some text that varies. The basement part 0 is "You've just sauntered into a basement.



You don't like doors? Why not try going east, that entranceway is unblocked.".
The description of r_19 is "[basement part 0]".

The r_14 is mapped east of r_19.
Understand "closet" as r_15.
The internal name of r_15 is "closet".
The printed name of r_15 is "-= Closet =-".
The closet part 0 is some text that varies. The closet part 0 is "You arrive in a closet. An usual kind of place.

 You make out a table. The table is normal.[if there is something on the s_2] On the table you make out [a list of things on the s_2].[end if]".
The closet part 1 is some text that varies. The closet part 1 is "[if there is nothing on the s_2] But there isn't a thing on it.[end if]".
The closet part 2 is some text that varies. The closet part 2 is " You make out a stand. [if there is something on the s_3]You see [a list of things on the s_3] on the stand.[end if]".
The closet part 3 is some text that varies. The closet part 3 is "[if there is nothing on the s_3]But there isn't a thing on it.[end if]".
The closet part 4 is some text that varies. The closet part 4 is "

You need an unguarded exit? You should try going south. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_15 is "[closet part 0][closet part 1][closet part 2][closet part 3][closet part 4]".

The r_14 is mapped west of r_15.
The r_17 is mapped south of r_15.
Understand "dish-pit" as r_16.
The internal name of r_16 is "dish-pit".
The printed name of r_16 is "-= Dish-Pit =-".
The dish-pit part 0 is some text that varies. The dish-pit part 0 is "You've just shown up in a dish-pit. The room is well lit.

 You can see a pan. The pan is normal.[if there is something on the s_4] On the pan you see [a list of things on the s_4].[end if]".
The dish-pit part 1 is some text that varies. The dish-pit part 1 is "[if there is nothing on the s_4] But there isn't a thing on it.[end if]".
The dish-pit part 2 is some text that varies. The dish-pit part 2 is " You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a platter. [if there is something on the s_5]You see [a list of things on the s_5] on the platter.[end if]".
The dish-pit part 3 is some text that varies. The dish-pit part 3 is "[if there is nothing on the s_5]However, the platter, like an empty platter, has nothing on it. Hopefully, this discovery doesn't ruin your TextWorld experience![end if]".
The dish-pit part 4 is some text that varies. The dish-pit part 4 is "

There is an exit to the north. Don't worry, it is unguarded. There is an exit to the south. Don't worry, it is unguarded. There is an exit to the west. Don't worry, it is unguarded.".
The description of r_16 is "[dish-pit part 0][dish-pit part 1][dish-pit part 2][dish-pit part 3][dish-pit part 4]".

The r_10 is mapped west of r_16.
The r_11 is mapped south of r_16.
The r_13 is mapped north of r_16.
Understand "garage" as r_17.
The internal name of r_17 is "garage".
The printed name of r_17 is "-= Garage =-".
The garage part 0 is some text that varies. The garage part 0 is "You've entered a garage. Let's see what's in here.

 You can see [if c_8 is locked]a locked[else if c_8 is open]an opened[otherwise]a closed[end if]".
The garage part 1 is some text that varies. The garage part 1 is " display nearby.[if c_8 is open and there is something in the c_8] The display contains [a list of things in the c_8].[end if]".
The garage part 2 is some text that varies. The garage part 2 is "[if c_8 is open and the c_8 contains nothing] The display is empty! What a waste of a day![end if]".
The garage part 3 is some text that varies. The garage part 3 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The garage part 4 is some text that varies. The garage part 4 is " passageway leading west. There is an unguarded exit to the north. There is an unblocked exit to the south.".
The description of r_17 is "[garage part 0][garage part 1][garage part 2][garage part 3][garage part 4]".

west of r_17 and east of r_13 is a door called d_0.
The r_18 is mapped south of r_17.
The r_15 is mapped north of r_17.
Understand "shower" as r_2.
The internal name of r_2 is "shower".
The printed name of r_2 is "-= Shower =-".
The shower part 0 is some text that varies. The shower part 0 is "You've just sauntered into a shower.



There is an unblocked exit to the east. You need an unguarded exit? You should try going north. You need an unguarded exit? You should try going south.".
The description of r_2 is "[shower part 0]".

The r_1 is mapped south of r_2.
The r_9 is mapped north of r_2.
The r_3 is mapped east of r_2.
Understand "cellar" as r_4.
The internal name of r_4 is "cellar".
The printed name of r_4 is "-= Cellar =-".
The cellar part 0 is some text that varies. The cellar part 0 is "You are in a cellar. An ordinary kind of place. You try to gain information on your surroundings by using a technique you call 'looking.'



You don't like doors? Why not try going east, that entranceway is unblocked. There is an exit to the north. Don't worry, it is unguarded. There is an unblocked exit to the west.".
The description of r_4 is "[cellar part 0]".

The r_1 is mapped west of r_4.
The r_3 is mapped north of r_4.
The r_5 is mapped east of r_4.
Understand "studio" as r_5.
The internal name of r_5 is "studio".
The printed name of r_5 is "-= Studio =-".
The studio part 0 is some text that varies. The studio part 0 is "You arrive in a studio.



You don't like doors? Why not try going east, that entranceway is unguarded. You don't like doors? Why not try going north, that entranceway is unblocked. You need an unblocked exit? You should try going west.".
The description of r_5 is "[studio part 0]".

The r_4 is mapped west of r_5.
The r_11 is mapped north of r_5.
The r_6 is mapped east of r_5.
Understand "forgotten vault" as r_6.
The internal name of r_6 is "forgotten vault".
The printed name of r_6 is "-= Forgotten Vault =-".
The forgotten vault part 0 is some text that varies. The forgotten vault part 0 is "You are in a vault. A forgotten one.

 You make out a chest![if c_10 is open and there is something in the c_10] The chest contains [a list of things in the c_10].[end if]".
The forgotten vault part 1 is some text that varies. The forgotten vault part 1 is "[if c_10 is open and the c_10 contains nothing] The chest is empty! What a waste of a day![end if]".
The forgotten vault part 2 is some text that varies. The forgotten vault part 2 is " You can see [if c_9 is locked]a locked[else if c_9 is open]an opened[otherwise]a closed[end if]".
The forgotten vault part 3 is some text that varies. The forgotten vault part 3 is " trunk close by.[if c_9 is open and there is something in the c_9] The trunk contains [a list of things in the c_9]. I mean, just wow! Isn't TextWorld just the best?[end if]".
The forgotten vault part 4 is some text that varies. The forgotten vault part 4 is "[if c_9 is open and the c_9 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The forgotten vault part 5 is some text that varies. The forgotten vault part 5 is "

There is an unguarded exit to the west.".
The description of r_6 is "[forgotten vault part 0][forgotten vault part 1][forgotten vault part 2][forgotten vault part 3][forgotten vault part 4][forgotten vault part 5]".

The r_5 is mapped west of r_6.
Understand "recreation zone" as r_8.
The internal name of r_8 is "recreation zone".
The printed name of r_8 is "-= Recreation Zone =-".
The recreation zone part 0 is some text that varies. The recreation zone part 0 is "You're now in the recreation zone.



There is an unblocked exit to the east. You need an unblocked exit? You should try going south.".
The description of r_8 is "[recreation zone part 0]".

The r_7 is mapped south of r_8.
The r_9 is mapped east of r_8.
Understand "bar" as r_18.
The internal name of r_18 is "bar".
The printed name of r_18 is "-= Bar =-".
The bar part 0 is some text that varies. The bar part 0 is "You've just walked into a bar. You start to take note of what's in the room.

 If you haven't noticed it already, there seems to be something there by the wall, it's a suitcase. You shudder, but continue examining the room.[if c_11 is open and there is something in the c_11] The suitcase contains [a list of things in the c_11]. I mean, just wow! Isn't TextWorld just the best?[end if]".
The bar part 1 is some text that varies. The bar part 1 is "[if c_11 is open and the c_11 contains nothing] The suitcase is empty, what a horrible day![end if]".
The bar part 2 is some text that varies. The bar part 2 is " You rest your hand against a wall, but you miss the wall and fall onto a bench. The bench is normal.[if there is something on the s_6] On the bench you see [a list of things on the s_6]. It doesn't get more TextWorld than this![end if]".
The bar part 3 is some text that varies. The bar part 3 is "[if there is nothing on the s_6] Looks like someone's already been here and taken everything off it, though. Aw, and here you were, all excited for there to be things on it![end if]".
The bar part 4 is some text that varies. The bar part 4 is "

You don't like doors? Why not try going north, that entranceway is unguarded.".
The description of r_18 is "[bar part 0][bar part 1][bar part 2][bar part 3][bar part 4]".

The r_17 is mapped north of r_18.
Understand "roomy vault" as r_7.
The internal name of r_7 is "roomy vault".
The printed name of r_7 is "-= Roomy Vault =-".
The roomy vault part 0 is some text that varies. The roomy vault part 0 is "You find yourself in a vault. A roomy kind of place. You start to take note of what's in the room.

 You see a case.[if c_12 is open and there is something in the c_12] The case contains [a list of things in the c_12]![end if]".
The roomy vault part 1 is some text that varies. The roomy vault part 1 is "[if c_12 is open and the c_12 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The roomy vault part 2 is some text that varies. The roomy vault part 2 is "

You don't like doors? Why not try going north, that entranceway is unblocked. There is an exit to the south. Don't worry, it is unblocked.".
The description of r_7 is "[roomy vault part 0][roomy vault part 1][roomy vault part 2]".

The r_0 is mapped south of r_7.
The r_8 is mapped north of r_7.

The c_0 and the c_1 and the c_10 and the c_11 and the c_12 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are containers.
The c_0 and the c_1 and the c_10 and the c_11 and the c_12 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are privately-named.
The d_0 and the d_1 are doors.
The d_0 and the d_1 are privately-named.
The k_0 are keys.
The k_0 are privately-named.
The o_0 are object-likes.
The o_0 are privately-named.
The r_1 and the r_0 and the r_10 and the r_9 and the r_11 and the r_3 and the r_13 and the r_12 and the r_14 and the r_19 and the r_15 and the r_16 and the r_17 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_18 and the r_7 are rooms.
The r_1 and the r_0 and the r_10 and the r_9 and the r_11 and the r_3 and the r_13 and the r_12 and the r_14 and the r_19 and the r_15 and the r_16 and the r_17 and the r_2 and the r_4 and the r_5 and the r_6 and the r_8 and the r_18 and the r_7 are privately-named.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 are supporters.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 are privately-named.

The description of d_0 is "it is what it is, a passageway [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_0 is "passageway".
Understand "passageway" as d_0.
The d_0 is open.
The description of d_1 is "it's a stuffy portal [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of d_1 is "portal".
Understand "portal" as d_1.
The d_1 is open.
The description of c_0 is "The crate looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_0 is "crate".
Understand "crate" as c_0.
The c_0 is in r_1.
The c_0 is open.
The description of c_1 is "The safe looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_1 is "safe".
Understand "safe" as c_1.
The c_1 is in r_10.
The c_1 is open.
The description of c_10 is "The chest looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_10 is "chest".
Understand "chest" as c_10.
The c_10 is in r_6.
The c_10 is locked.
The description of c_11 is "The suitcase looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_11 is "suitcase".
Understand "suitcase" as c_11.
The c_11 is in r_18.
The c_11 is open.
The description of c_12 is "The case looks strong, and impossible to break. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_12 is "case".
Understand "case" as c_12.
The c_12 is in r_7.
The c_12 is locked.
The description of c_2 is "The portmanteau looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_2 is "portmanteau".
Understand "portmanteau" as c_2.
The c_2 is in r_9.
The c_2 is open.
The description of c_3 is "The fridge looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "fridge".
Understand "fridge" as c_3.
The c_3 is in r_3.
The c_3 is locked.
The description of c_4 is "The box looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_4 is "box".
Understand "box" as c_4.
The c_4 is in r_13.
The c_4 is closed.
The description of c_5 is "The coffer looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_5 is "coffer".
Understand "coffer" as c_5.
The c_5 is in r_13.
The c_5 is open.
The description of c_6 is "The basket looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_6 is "basket".
Understand "basket" as c_6.
The c_6 is in r_12.
The c_6 is closed.
The description of c_7 is "The cabinet looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_7 is "cabinet".
Understand "cabinet" as c_7.
The c_7 is in r_12.
The c_7 is closed.
The description of c_8 is "The display looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_8 is "display".
Understand "display" as c_8.
The c_8 is in r_17.
The c_8 is locked.
The description of c_9 is "The trunk looks strong, and impossible to destroy. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_9 is "trunk".
Understand "trunk" as c_9.
The c_9 is in r_6.
The c_9 is closed.
The description of k_0 is "The latchkey is light.".
The printed name of k_0 is "latchkey".
Understand "latchkey" as k_0.
The k_0 is in r_11.
The description of o_0 is "The bug is unremarkable.".
The printed name of o_0 is "bug".
Understand "bug" as o_0.
The o_0 is in r_15.
The description of s_0 is "The counter is solidly built.".
The printed name of s_0 is "counter".
Understand "counter" as s_0.
The s_0 is in r_14.
The description of s_1 is "The shelf is shaky.".
The printed name of s_1 is "shelf".
Understand "shelf" as s_1.
The s_1 is in r_14.
The description of s_2 is "The table is wobbly.".
The printed name of s_2 is "table".
Understand "table" as s_2.
The s_2 is in r_15.
The description of s_3 is "The stand is an unstable piece of garbage.".
The printed name of s_3 is "stand".
Understand "stand" as s_3.
The s_3 is in r_15.
The description of s_4 is "The pan is reliable.".
The printed name of s_4 is "pan".
Understand "pan" as s_4.
The s_4 is in r_16.
The description of s_5 is "The platter is unstable.".
The printed name of s_5 is "platter".
Understand "platter" as s_5.
The s_5 is in r_16.
The description of s_6 is "The bench is an unstable piece of junk.".
The printed name of s_6 is "bench".
Understand "bench" as s_6.
The s_6 is in r_18.


The player is in r_19.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.

Test quest0_0 with "go east / go south / go west / go south / go south / go south / go east / go north / take latchkey"

Every turn:
	if quest0 completed is true:
		do nothing;
	else if The player carries the o_0:
		end the story; [Lost]
	else if The player is in r_11 and The player carries the k_0:
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

The objective part 0 is some text that varies. The objective part 0 is "You are now playing a exciting session of TextWorld! First off, move east. And then, attempt to go to the south. With that accomplished, attempt to move west. And then, move south. And then, make an e".
The objective part 1 is some text that varies. The objective part 1 is "ffort to head south. With that done, make an attempt to go south. And then, go east. And then, try to move north. With that accomplished, pick up the latchkey from the floor of the spare room. Once th".
The objective part 2 is some text that varies. The objective part 2 is "at's all handled, you can stop!".

An objective is some text that varies. The objective is "[objective part 0][objective part 1][objective part 2]".
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

