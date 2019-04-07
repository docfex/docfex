# Contributing
Docfex is in early development, so any kind of contribution is welcome.

## Code style
* Try to adhere to the SOLID principles and keep your code DRY.
* Name variables, functions and classes so they are self explanatory and need no comments.
* Functions and classes used in more than one file must be commented.


## Focus
**1. Testing**</br>
At the moment docfex doesn't have any kind of automated testing.
Since docfex basically is a gateway between Flask and Elasticsearch, there is not much room for normal UnitTests. Since I am not yet familiar with moqs in python, help in regards of testing is very much appreciated.

**2. Logging**</br>
Besides testing, logging should also be improved. 
Currently information is simply outputted using print().


**Note:** Until testing and logging is not improved, no other features are added!


