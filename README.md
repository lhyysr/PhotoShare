# PhotoShare
An online photo social network system

# Purpose of the project
In this project, you will design, implement and document a database system for a web based photo social sharing application. You need also to provide the web based interface to the database. The final system should be functional and will be similar to Flickr!

# Data
__Users__
Each user is identified by a unique user id and has the following attributes: first name, last name, email, date of birth, hometown, gender, and password. A user can have a number of Albums.
__Friends__
Each user can have any number of friends.
__Albums__
Each album is identified by a unique album id and has the following attributes: name, owner (user) id, and date of creation. Each album can contain a number of photos.
__Photos__
Each photo is identified by a unique photo id and must belong to an album. Each photo has the following attributes: caption and data. The 'data' field should contain the actual binary representation of the uploaded image file. Alternatively, the 'data' field can store the file location of the file that stores the image. Each photo can only be stored in one album and is associated with zero, one, or more tags.
__Tags__
Each tag is described by a single word. Many photos can be tagged with the same tag. For the purpose of this project we will assume that all tags are lowercased and contain no spaces. For example, you can have many photos tagged with the tag "boston" in different albums.
__Comments__
Each comment is identified by a unique comment id and has the following attributes: text (i.e., the actual comment), the comment's owner (a user) and the date the comment was left.

# Functionalities
__Becoming a registered user__
Before being able to upload photos a user should register by providing their first name, last name, email address, date of birth, and a password. If the user already exists in the database with the same email address an error message should be produced. The other additional information about each user is optional.
__Adding and Listing Friends__
You should allow a user to add a new friend on the friend list. For simplicity, you do not have to verify the friendship relationship. Also, you should allow the user to search for other users in the system (in order to find friends to add.) Finally, you must allow a user to list his/her friends.
__User activity__
To motivate users in using the site we'd like to identify the ones who make the largest contribution and list them on the site. We'll measure the contribution of a user as the number of photos they have uploaded plus the number of comments they have left for photos belonging to other users. The top 10 users should be reported.
__Photo and album browsing__
Every visitor to the site, registered or not, should be allowed to browse photos. In this project we will assume that all photos and albums are made public by their authors.
__Photo and album creating__
After registration, users can start creating albums and uploading photos. The relevant fields are described above. Users should also be able to delete both albums and photos. If an nonempty album is deleted its photos should also be purged. Users should only be allowed to modify and delete albums and photos which they own.
__Viewing your photos by tag name__
Tags provide a way to categorize photos and each photo can have any number of tags. You may think of them as virtual albums. For example, suppose that a user has two distinct albums each of which contains a photo with the tag 'friends'. The means should be provided to view the virtual album created if we select all the photos owned by the user that contain the tag 'friends'. One possible user interface design for this functionality is to present tags as hyperlinks. When a tag is clicked the photos tagged with it are listed.
__Viewing all photos by tag name__
Furthermore, the system should allow users to view all photos that contain a certain tag, i.e., not only the ones they have uploaded but also photos that belong to other users. This functionality is similar to the one above and hence they could be presented together. One possible representation is a switch of the form "View all photos / View my photos" that when toggled switches from one view to the other.
__Viewing the most popular tags__
A function should be provided that lists the most popular tags, i.e., the tags that are associated with the most photos. Again, tags should be clickable so that when a user clicks one of them all photos tagged with this tag are listed.
__Photo search__
The functionality should be provided so that both visitors and registered users can search through the photos by specifying conjunctive tag queries. For example a visitor could enter the words "friends boston" in a text field, click the search button and be presented with all photos that contain both the tag "friends" and the tag "boston".
__Leaving comments__
Both registered and anonymous users can leave comments. Users cannot leave comments for their own photos. If registered user leaves a comment then this counts towards their contribution score as described above.
__Like functionality__
We want to add a Like functionality. If a user likes a photo, should be able to add a like to the photo. Also, we must be able to see how many likes a photo has and the users that liked this photo.
__Youmayalsolike__
Given the type of photos uploaded by a user we'd like to make some recommendations to them about other photos they may like. To achieve that do the following: Take the five most commonly used tags among the user's photos. Perform a disjunctive search through all the photos for these five tags. A photo that contains all five tags should be ranked higher than one that contained four of the tags and so on. Between two photos that contain the same number of matched tags prefer the one that is more concise, i.e., the one that has fewer tags over all.
__Tag recommendation__
We want to assist users in selecting tags for their photos. To do that ask the user to enter a couple of tags that they already have in mind. Perform a query and find all the photos, belonging to any user, that contain these tags. Take the tags of these photos in the result set and order them by frequency of occurrence (obviously you have to exclude the tags that were part of the query). Report back the most frequent tags as recommendations.
