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

2. Voting Page - Display the title and text of the current law.  Allow for citizens to see other citizens comments on the legislation and vote.

3. Established Laws - Allows for each citizen to be informed on already passed laws.

4. Proposed Bills - Allows for each citizen to search for bills that may interest them, and donate to these bills.

5. Draft Laws - Allows citizens to draft and submit laws to the blockchain.

6. Manage Connections - Allows for citizens to connect to other mining nodes, increasing the security of the blockchain.


The current code for this prototype of blockchain legislation is minimalist.  Excitingly, through adopting the approach of allowing citizens to participate in the legislative process with modern technology innovations on the democratic process are possible.  I will list a few obvious examples here.
1. Bill Search Algorithm - How to identify which bills an individual may be searching for? Possible improvements with vector search.
2. Law Search Engine - Search engine to better find already passed laws that a citizen may like to be informed on.
3. Suggested Bills - Notify individuals of bills which other citizens of similar voting/donation history have donated to.  This can help organize citizens around popular issues.
4. LLMs for Draft Editing - Help a citizen properly word legislation with fine-tuned LLMs.
5. Citizen No Confidence Vote - In the case of representative abuse of power, citizens could vote to enter an emergency mode of the blockchain protocol, where laws are passed more quickly to help citizens organize against threats to their democracy.
6. Citizen Comments For and Against Legislation - Citizens can comment on legislation as they vote on it, to provide evidence for their view.  Additionally citizens can upvote helpful comments for others to see useful evidence.
7. QR Codes for checking their vote on other citizens devices - Allow for citizens to validate that their vote has made it to another individual's device and is being counted.
