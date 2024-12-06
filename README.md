This project contains the code for a Kivy App which creates a prototype of secure way for citizens to both draft and vote on legislation, without the need for intermediate representatives.  This is a generalization of blockchain technology to legislation, which notably has previously been used for voting. 


The blockchain citizen legistation system is described below.
1. Private keys are distributed by the government, similar to state issued IDs.
2. Citizens use these private keys in a phone app to draft bills.  Any citizen can draft a new bill.
3. During a voting period, citizens donate political cryptocoin to bills that they would like to bring to a vote.  This political cryptocoin is not mineable.
4. In regular intervals, the citizens will be able to vote on the bill with the most policital coin.
5. After voting, the political coin associated with the bill will be redistributed to all citizens who voted.
6. If the bill passes then it becomes law, if not then it does not.

Through the state issuance of private keys, each person is able to vote only once on each bill.  Additionally, only citizens are able to be miners, which consensus algorithms can take advantage of in order to make sure that the miners of the blockchain are representative of the population, through increasing the difficulty of hashing if small groups of miners are dominating the chain.

The blockchain can either be supported by volunteers, or by a traditional cryptocurrency which is added to the blockchain.  This current version of the code implements a traditional cryptocurrency which rewards citizens for maintaining the legislative blockchain.




The app has several pages.
1. Homepage - Display relevant information such as the user's political cryptocurrency, and the current bill which is being voted on.
![Homepage](https://github.com/user-attachments/assets/1251f511-17f8-4da8-8aa0-19fa1d30a349)

2. Voting Page - Display the title and text of the current law.  Allow for citizens to see other citizens comments on the legislation and vote.
![VotingPage](https://github.com/user-attachments/assets/6bb8f443-ca47-4f99-aeaf-7b376737d161)

3. Proposed Bills - Allows for each citizen to search for bills that may interest them, and donate to these bills.
![BillSearch](https://github.com/user-attachments/assets/da2e78f2-5fb7-4287-828e-6b73e8fc801a)

4. Established Laws - Allows for each citizen to be informed on already passed laws.
![EstablishedLawsPage](https://github.com/user-attachments/assets/cbd9315a-0015-4762-8925-fcee47e0f369)

5. Draft Laws - Allows citizens to draft and submit laws to the blockchain.
![LawDraftPage](https://github.com/user-attachments/assets/2fee2e4a-a5e2-4924-b51f-b81c0d514f22)

7. Manage Connections - Allows for citizens to connect to other mining nodes, increasing the security of the blockchain.
![ManageConnections](https://github.com/user-attachments/assets/73452684-f25c-4385-b183-ed1858b026f2)


The current code for this prototype of blockchain legislation is minimalist.  Excitingly, through adopting the approach of allowing citizens to participate in the legislative process with modern technology innovations on the democratic process are possible.  I will list a few obvious examples here.
1. Bill Search Algorithm - How to identify which bills an individual may be searching for? Possible improvements with vector search.
2. Law Search Engine - Search engine to better find already passed laws that a citizen may like to be informed on.
3. Suggested Bills - Notify individuals of bills which other citizens of similar voting/donation history have donated to.  This can help organize citizens around popular issues.
4. LLMs for Draft Editing - Help a citizen properly word legislation with fine-tuned LLMs.
5. Citizen No Confidence Vote - In the case of representative abuse of power, citizens could vote to enter an emergency mode of the blockchain protocol, where laws are passed more quickly to help citizens organize against threats to their democracy.
6. Citizen Comments For and Against Legislation - Citizens can comment on legislation as they vote on it, to provide evidence for their view.  Additionally citizens can upvote helpful comments for others to see useful evidence.
7. QR Codes for checking their vote on other citizens devices - Allow for citizens to validate that their vote has made it to another individual's device and is being counted.




The code for this project works on both Windows and Android.  However, I have experienced some bugs with certain android phones and pixel versions, likely due to the Kivy version used.  This app was tested on a Pixel 6 with Android Version 15.  The .apk package is included in the bin folder.  The python library requirements are included in pipfreeze.txt.  Also note, Android phones cannot be miners, only a windows machine can become a miner.

To run on windows, 
1. pip install the requirements in pipfreeze.txt
2. Navigate into the folder.
3. Run python main.py
4. If windows asks for permissions for python to use the local network then accept. 
5. Once the app appears, click the menu icon on the top left.
6. Navigate to "make connections".
7. Click become server (begins mining).
8. Note the IP address displayed above this button.  This will need to be entered into your phone later to make a connection.


To run on Android,
1. Load the .apk file found on the bin folder onto the phone (Google drive or over USB)
2. Run the .apk file on the phone using package installer.
3. Run the App (if it crashes it is likely due to Kivy not compatible with Android device)
4. Navigate to "Make Connections"
5. Enter the IP Address found above.
6. Click connect
7. Navigate to Draft Laws and draft a law (and click the submit button)
8. Wait 20 seconds for the blockchain to sync
9. Click on the homepage and the law should be there
10. Click on the Voting page and write a comment and vote
11. Wait 10 minutes (this is the default voting period)
12. Navigate to Establised Laws and search for your law's title
13. The law should be visible now in established laws.

Congratulations!  You have now formed a distributed legislative body.  Innovate on this approach and bring it into the world!!!
