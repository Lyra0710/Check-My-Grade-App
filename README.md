# Check-My-Grade-App

## Unit Testing
- Testing of student records addition/deletion and modification. Performing the test to have the
student files atleast 1000 records.
- Loading the data from previous runs saved in the csv files and loading the data
and search. Printing the time taken for search cases. 
- Test case to sort the student records (ascending/descending order) based on
marks or student email_address. Report includes the timing it took to sort the records. 
- Unit test to add/delete/modify the course , professor

### My Learning for Unit Testing:
- Learning about the unittest module. 
- Creating a test class. Here I created BasicTests class. 
- The test methods should start with a `test_`. 
- We write the code that will show the expected result, then compare it with the actual result using `assertion methods`. # Check-My-Grade-App
- The function test_search_timing_basic() reads the students saved in file and searches based on email and id. 
- The time taken to search is printed by using the `time.perf_counter` function with timestamps taken at different sections (difference sorting orders). 