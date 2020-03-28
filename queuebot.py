import discord, os
from discord.ext import commands
from copy import copy

prefix = "!"
client = commands.Bot(command_prefix=prefix)

Nchannels = 4
channel_names = ('Alpha','Beta','Gamma','Delta','Epsilon','Zeta','Omega','Kappa','Lambda','Theta','Sigma','Iota','Omicron',
    'Mu','Nu','Xi','Pi','Rho','Tau','Upsilon','Phi','Chi','Psi','Eta')

queuebot_role = 'queuebot'
approved_roles = ['Tutor']

tutor_permissions = {
    'add_reactions': True, 'administrator': True, 'attach_files': True, 'ban_members': False, 'change_nickname': True, 'connect': True, 
'create_instant_invite': True, 'deafen_members': True, 'embed_links': True, 'external_emojis': True, 'kick_members': True, 
'manage_channels': True, 'manage_emojis': True, 'manage_guild': True, 'manage_message':True,'manage_nicknames':False,
'manage_permissions':True,'manage_roles':True,'manage_webhooks':True,'mention_everyone':True,'move_members':True,'mute_members':True,
'priority_speaker':False,'read_message_history':True,'read_messages':True,'send_messages':True,'send_tts_messages':True,'speak':True,
'stream':True,'use_external_emojis':True,'use_voice_activation':True,'view_audit_log':True,'view_channel':True,'view_guild_insights':True}
tutor_permission_obj = discord.Permissions()
tutor_permission_obj.update(**tutor_permissions)

meeting_permissions = {
    'add_reactions': False, 'administrator': False, 'attach_files': False, 'ban_members': False, 'change_nickname': False, 'connect': False, 
'create_instant_invite': False, 'deafen_members': False, 'embed_links': False, 'external_emojis': False, 'kick_members': False, 
'manage_channels': False, 'manage_emojis': False, 'manage_guild': False, 'manage_message':False,'manage_nicknames':False,
'manage_permissions':False,'manage_roles':False,'manage_webhooks':False,'mention_everyone':False,'move_members':False,'mute_members':False,
'priority_speaker':False,'read_message_history':False,'read_messages':False,'send_messages':False,'send_tts_messages':False,'speak':False,
'stream':True,'use_external_emojis':False,'use_voice_activation':True,'view_audit_log':False,'view_channel':False,'view_guild_insights':False}
meeting_permission_obj = discord.Permissions()
meeting_permission_obj.update(**meeting_permissions)

tr_ow_t = discord.PermissionOverwrite()
tr_ow_t.update(**{'read_messages':True})
qbr_ow_t = discord.PermissionOverwrite()
qbr_ow_t.update(**{'read_messages':True})
mr_ow_t = discord.PermissionOverwrite()
mr_ow_t.update(**{'read_messages':True,'send_message':True,'embed_links':True,'attach_files':True,
    'read_message_history':False,'add_reactions':True})
er_ow_t = discord.PermissionOverwrite()
er_ow_t.update(**{'read_messages':False})

tr_ow_v = discord.PermissionOverwrite()
tr_ow_v.update(**{'create_instant_invite':True,'manage_channels':True,'manage_permissions':True,'manage_webhooks':True,
    'view_channel':True,'connect':True,'speak':True,'mute_members':True,'deafen_members':True,'move_members':True,
    'use_voice_activation':True,'stream':True})
qbr_ow_v = discord.PermissionOverwrite()
qbr_ow_v.update(**{'view_channel':True,'move_members':True})
mr_ow_v = discord.PermissionOverwrite()
mr_ow_v.update(**{'create_instant_invite':False,'manage_channels':False,'manage_permissions':False,'manage_webhooks':False,
    'view_channel':True,'connect':True,'speak':True,'mute_members':False,'deafen_members':False,'move_members':False,
    'use_voice_activation':True,'stream':True})
er_ow_v = discord.PermissionOverwrite()
er_ow_v.update(**{'create_instant_invite':False,'manage_channels':False,'manage_permissions':False,'manage_webhooks':False,
    'view_channel':False,'connect':False,'speak':False,'mute_members':False,'deafen_members':False,'move_members':False,
    'use_voice_activation':False,'priority_speaker':False,'stream':False})

er_ow_wt = discord.PermissionOverwrite()
er_ow_wt.update(**{'create_instant_invite':False,'manage_channels':False,'manage_permissions':False,'manage_webhooks':False,
    'read_messages':True,'send_message':False,'send_tts_messages':False,'manage_messages':False,'embed_links':False,
    'attach_files':False,'read_message_history':True,'mention':False,'use_external_emojis':False,'add_reactions':False})

er_ow_ch = discord.PermissionOverwrite()
er_ow_ch.update(**{'create_instant_invite':False,'manage_channels':False,'manage_permissions':False,'manage_webhooks':False,
    'read_messages':True,'send_message':True,'send_tts_messages':False,'manage_messages':False,'embed_links':True,
    'attach_files':True,'read_message_history':True,'mention':False,'use_external_emojis':True,'add_reactions':True})   

er_ow_ad = discord.PermissionOverwrite()
er_ow_ad.update(**{'read_messages':False})
qbr_ow_ad = discord.PermissionOverwrite()
qbr_ow_ad.update(**{'read_messages':True,'send_messages':True})
tr_ow_ad = discord.PermissionOverwrite()
tr_ow_ad.update(**{'read_messages':True,'send_messages':True})

tr_ow_wr = discord.PermissionOverwrite()
tr_ow_wr.update(**{'view_channel':True,'connect':True,'speak':True,'move_members':True})
er_ow_wr = discord.PermissionOverwrite()
er_ow_wr.update(**{'create_instant_invite':False,'manage_channels':False,'manage_permissions':False,'manage_webhooks':False,
    'view_channel':True,'connect':True,'speak':False,'mute_members':False,'deafen_members':False,'move_members':False,
    'use_voice_activation':False,'stream':False})

spam_channels = ['spam']
waiting_room = 'Waiting Room'
queue_channel = 'queue'

@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(activity=discord.Game(name='Queuing Fun'))

def is_approved():
    def predicate(ctx):
        author = ctx.message.author
        if author is ctx.guild.owner:
            return True
        if any(role.name in approved_roles for role in author.roles):
            return True
    return commands.check(predicate)

def is_spam():
    def predicate(ctx):
        channel = ctx.channel
        if channel.name in spam_channels:
            return True
    return commands.check(predicate)

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.qtoggle = False

    @commands.command(pass_context=True)
    async def add(self, ctx):
        ''': Add yourself to the queue!'''
        author = ctx.author
        if self.qtoggle:
            if author.id not in self.queue:
                self.queue.append(author.id)
                await ctx.send(f'{author.mention}: You have been added to the queue. Please enter the Waiting Room.')
            else:
                await ctx.send(f'{author.mention}: You are already in the queue!')
        else:
            await ctx.send('The queue is closed.')
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def remove(self, ctx):
        ''': Remove yourself from the queue'''
        author = ctx.author
        if author.id in self.queue:
            self.queue.remove(author.id)
            await ctx.send(f'{author.mention}: You have been removed from the queue.')
        else:
            await ctx.send(f'{author.mention}: You were not in the queue.')
        await ctx.message.delete()

    @is_spam()
    @commands.command(name='queue', pass_context=True)
    async def _queue(self, ctx):
        ''': See who's up next!'''
        server = ctx.guild
        message = ''
        for place, member_id in enumerate(self.queue):
            if place > 4:
                break
            member = discord.utils.get(server.members, id=member_id)
            message += f'**#{place+1}** : {member.mention}\n'
        if message != '':
            await ctx.send(message)
        else:
            await ctx.send('Queue is empty')
        await ctx.message.delete()

    @is_spam()
    @commands.command(pass_context=True)
    async def position(self, ctx):
        ''': Check your position in the queue'''
        author = ctx.author
        if author.id in self.queue:
            _position = self.queue.index(author.id)+1
            await ctx.send(f'{author.mention}: You are **#{_position}** in the queue.')
        else:
            await ctx.send(f'{author.mention}: You are not in the queue, please use {prefix}add to add yourself to the queue.')
        await ctx.message.delete()

    @is_approved()
    @commands.command(pass_context=True, name='next')
    async def _next(self, ctx):
        ''': Call the next member in the queue'''
        if len(self.queue) > 0:
            member = discord.utils.get(
                ctx.guild.members, id=self.queue[0])
            channel = discord.utils.get(ctx.guild.text_channels, name=queue_channel)
            await channel.send(f'You are up **{member.mention}**! Please join channel **{member.roles[-1]}**.')
            self.queue.remove(self.queue[0])
        await ctx.message.delete()

    @is_approved()
    @commands.command(pass_context=True, name='bye')
    async def _bye(self, ctx):
        role = [s for s in ctx.guild.roles 
                if s.name.lower()==ctx.channel.name.lower()][0]
        waiting_room_obj = discord.utils.get(ctx.guild.voice_channels, name=waiting_room)
        for member in role.members:
            await member.remove_roles(role)
            await member.move_to(waiting_room_obj)

    @is_approved()
    @commands.command(pass_Context=True, name='pull')
    async def _pull(self, ctx):
        if len(self.queue) > 0:
            member = discord.utils.get(
                ctx.guild.members, id=self.queue[0])
            role = [s for s in ctx.guild.roles 
                    if s.name.lower()==ctx.channel.name.lower()][0]
            await member.add_roles(role)
            await ctx.send(f'{member.nick} is up next')
            await self._next(ctx)
        else:
            await ctx.send('Queue is empty')

    @is_approved()
    @commands.command(pass_context=True)
    async def clear(self, ctx):
        ''': Clears the queue'''
        self.queue = []
        await ctx.send('Queue has been cleared')

    @is_approved()
    @commands.command(pass_context=True)
    async def toggle(self, ctx):
        ''': Toggles the queue'''
        self.qtoggle = not self.qtoggle
        if self.qtoggle:
            state = 'OPEN'
        else:
            state = 'CLOSED'
        await ctx.send(f'Queue is now {state}')
        qchannel = discord.utils.get(ctx.guild.text_channels, name=queue_channel)
        if ctx.channel != qchannel:
            await qchannel.send(f'Queue is now {state}')
    
    @is_approved()
    @commands.command(pass_context=True)
    async def start(self, ctx):
        ''': Sets up roles and channels'''
        # check Queuebot has permissions to do its job
        if not any(role.name.lower() == queuebot_role for role in ctx.guild.roles):
            raise ValueError('Cannot find Queuebot role.')
        qbr = [role for role in ctx.guild.roles if role.name.lower() == queuebot_role][0]
        qb = [member for member in ctx.guild.members if member.name.lower() == queuebot_role][0]
        if qbr not in qb.roles:
            raise ValueError('Queuebot role not assigned to queuebot')

        # remove general channels if existing
        gt = discord.utils.get(ctx.guild.text_channels, name='general')
        if gt:
            await gt.delete()
        gt = discord.utils.get(ctx.guild.voice_channels, name='General')
        if gt:
            await gt.delete()

        # create Roles if not already existing
        if not discord.utils.get(ctx.guild.roles, name='Tutor'):
            await ctx.guild.create_role(name='Tutor', permissions = tutor_permission_obj, hoist=True)
        tr = discord.utils.get(ctx.guild.roles, name='Tutor')
        er = discord.utils.get(ctx.guild.roles, name='@everyone')

        # create meeting rooms if not already existing
        if not discord.utils.get(ctx.guild.categories, name='Meeting Rooms'):
            await ctx.guild.create_category('Meeting Rooms')
        mct = discord.utils.get(ctx.guild.categories, name='Meeting Rooms')
        tct = discord.utils.get(ctx.guild.categories, name='Text Channels')
        vct = discord.utils.get(ctx.guild.categories, name='Voice Channels')
        
        text_overwrites = {tr:tr_ow_t, qbr:qbr_ow_t, er:er_ow_t}
        voice_overwrites = {tr:tr_ow_v, qbr:qbr_ow_v, er:er_ow_v}
        for channel_name in channel_names[:Nchannels]:
            # create role
            if not discord.utils.get(ctx.guild.roles, name=channel_name):
                await ctx.guild.create_role(name = channel_name, permissions = meeting_permission_obj)
            mr = discord.utils.get(ctx.guild.roles, name=channel_name)

            # create text channel
            channel_overwrites = copy(text_overwrites)
            channel_overwrites.update({mr:mr_ow_t})
            if not discord.utils.get(ctx.guild.text_channels, name=channel_name.lower()):
                await ctx.guild.create_text_channel(name = channel_name.lower(), category=mct, overwrites=channel_overwrites)
                
            # create voice channel
            channel_overwrites = copy(voice_overwrites)
            channel_overwrites.update({mr:mr_ow_v})
            if not discord.utils.get(ctx.guild.voice_channels, name=channel_name):
                await ctx.guild.create_voice_channel(name = channel_name, category=mct, overwrites=channel_overwrites)

        # create queue/welcome/chatter/admin/Waiting Room channels
        if not discord.utils.get(ctx.guild.text_channels, name='welcome'):
            await ctx.guild.create_text_channel(name = 'welcome', overwrites={er:er_ow_wt}, category=tct)
            wt = discord.utils.get(ctx.guild.text_channels, name='welcome')
            with open('welcome.txt','r') as fp:
                await wt.send(''.join(fp.readlines()))
        if not discord.utils.get(ctx.guild.text_channels, name='chatter'):
            await ctx.guild.create_text_channel(name = 'chatter', overwrites={er:er_ow_ch}, category=tct)
        if not discord.utils.get(ctx.guild.text_channels, name='queue'):
            await ctx.guild.create_text_channel(name = 'queue', category=tct)
        if not discord.utils.get(ctx.guild.text_channels, name='spam'):
            await ctx.guild.create_text_channel(name = 'spam', category=tct)
        if not discord.utils.get(ctx.guild.text_channels, name='admin'):
            await ctx.guild.create_text_channel(name = 'admin', overwrites={er:er_ow_ad,qbr:qbr_ow_ad,tr:tr_ow_ad}, category=tct)
        if not discord.utils.get(ctx.guild.voice_channels, name='Waiting Room'):
            await ctx.guild.create_voice_channel(name = 'Waiting Room', overwrites={er:er_ow_wr,tr:tr_ow_wr}, category=vct)

        await self.toggle(ctx)   
        return

client.add_cog(Queue(client))

if __name__ == "__main__":
    if os.path.isfile('../mytoken.txt'):
        with open('../mytoken.txt', 'r') as fp:
            tkn = ''.join(fp.readlines()).replace('\n','')
    else:
        raise FileNotFoundError("Cannot find token file '../mytoken.txt'")
    client.run(tkn)
