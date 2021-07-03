# A Python-Powered Twitch Chatbot. 
### An all-in-one Twitch engagement and analytics project, [built live on stream](https://twitch.tv/MitchsWorkshop). 
Just add your credentials and go. 
  
## 🤖 Using the bot ##  
1. Get a Client ID and Client Secret [from Twitch](https://dev.twitch.tv/api/).
2. Get an Oauth token [here](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth).
3. Fill `credentials.env.sample` with the above tokens, as well as the name of the bot and the channel it will join.
4. Rename `credentials.env.sample` -> `credentials.env`
5. Run `chat_bot.py`.
6. In Twitch chat, add, edit, or delete commands with `!addcommand`, `!editcommand`, or `!delcommand` respectively.
  
## 🖥 Data Gathering ##  
The bot will store data in a PostgreSQL database called `stream_data` which is created by the bot at startup. It 
stores every message sent, and every command used. Additional insights about stream length, title, average viewership, 
new followers/subscribers, cheers, tips, and other data points are in the works.  
  
## 🏡 Hosted Locally. ##  
All of the data the bot gathers is stored locally. Keep in mind that no one can hide Twitch data from Twitch itself. 
Still, there is no need to rely on third party bots like StreamElements or StreamLabs to gain access to your chat data, 
and you won't have to slog through Twitch's terrible analytics. The data is all yours, in real time. Once the data viz
app is constructed, there will be no programming knowledge required to get these insights.
  
## 🎥 Built On Stream ##  
If you want to see the progress on this project being made live, feel free to come by my own [Twitch channel](https://twitch.tv/MitchsWorkshop) 
to ask questions or comment on the code. When I'm offline, feel free to reach out on the Workshop [Discord Server](https://discord.gg/7nefPK6) 
and offer up your questions, comments, critiques, or feature proposals. There are hundreds people in there who love to 
help give advice. It's a fun place that I'm proud of. Thanks, friends!
