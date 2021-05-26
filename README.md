# A Python-Powered Twitch Chatbot. 
### An all-in-one Twitch engagement and analytics project, [built live on stream](https://twitch.tv/MitchsWorkshop). Just add your credentials and go. 
  
## 🤖 Using the bot ##  
Currently, there is a working custom chat bot that requires users to create a `credentials.env` file and pass in the account name of their bot, its Client ID (recieved from the [Twitch developer portal](https://dev.twitch.tv/api/)), and an OAuth token ([also from Twitch](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth)). The bot will run with some default commands, and users can add, edit, or delete their own with `!addcommand`, `!editcommand`, and `!delcommand`.  
  
## 🖥 Data Gathering ##  
The bot will store data in a SQLite database called `data.db` which is created by the bot at startup. It stores every message sent (the sender and the time of sending, not the content of the message), and every command used. In the works is the ability to track per-minute viewership, average view time per viwer, whether or not those viewers are followers/subscribers, and who is chatting or not. This will help content creators focus their efforts where they are weakest. Additional insights about stream length, title, average viewership, new followers/subscribers, cheers, tips, and other data points will also be included.    
  
## 🏡 Hosted Locally. Your Data is Yours. ##  
Since all of the data is stored locally, you can be confident in the persistance of your data. Keep in mind, however, no one can hide Twitch data from Twitch itself. Still, there is no need to rely on third party bots like StreamElements or StreamLabs to gain access to your chat data, and you won't have to slog through Twitch's terrible analytics process. The data is all yours, in real time. No programming knowedge required.  
  
## 🎥 Built On Stream ##  
If you want to see the progress on this project being made live, feel free to come by my own [Twitch channel](https://twitch.tv/MitchsWorkshop) to ask questions or comment on the code. When I'm offline, feel free to reach out on the Workshop [Discord Server](https://discord.gg/7nefPK6) and offer up your questions, comments, critiques, or feature proposals. There are a couple hundred people in there who love to help each other with problems or give programming advice. It's a fun place that I'm proud of. Thanks, friends!
