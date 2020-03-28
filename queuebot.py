import discord, os
from discord.ext import commands
from copy import copy
import yaml
import sys

# Load and update defaults with config file specified in inputs
with open('defaults.yml', 'r') as defaults_file:
    config = yaml.load(defaults_file, Loader=yaml.CLoader)
if len(sys.argv) > 1 and not sys.argv[1][:2] == "--":
    with open(sys.argv[1], 'r') as config_file:
        config_update = yaml.load(config_file, Loader=yaml.CLoader)
        for field, values in config_update.items():
            if field in config:
                config[field].update(values)
            else:
                config[field] = values

def get_permissions(name, overwrite=True):
    """ Parses permissions from the ingested config dictionary """
    permission_list = {p:bool(b) for b, ps in config['permissions'][name].items() for p in ps}
    if overwrite:
        permission_obj = discord.PermissionOverwrite()
    elif not overwrite:
        permission_obj = discord.Permissions()
    permission_obj.update(**permission_list)
    return permission_obj

#---------------------------------------------
# Permission check functions
#---------------------------------------------

def _approved_(ctx):
    author = ctx.message.author
    if author is ctx.guild.owner:
        return True
    if any(role.name in config['approved_roles'] for role in author.roles):
        return True

def _spam_(ctx):
    channel = ctx.channel
    if channel.name in config['spam_channels']:
        return True

def _owner_(ctx):
    owner = ctx.guild.owner
    if ctx.author == owner:
        return True

def is_approved():
    return commands.check(_approved_)

def is_spam():
    return commands.check(_spam_)

def is_starter():
    def predicate(ctx):
        return _approved_(ctx) or _owner_(ctx)
    return commands.check(predicate)

class Queue(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.queue = []
        self.qtoggle = False
        self.config = config['queuebot']
        self.role = self.config['role']

    @is_starter()
    @commands.command(pass_context=True)
    async def start(self, ctx):
        ''': Sets up roles and channels'''
        # check Queuebot has permissions to do its job
        if not any(role.name.lower() == self.role.lower() for role in ctx.guild.roles):
            raise ValueError(f'Cannot find Queuebot role: {self.role}.')
        qbr = [role for role in ctx.guild.roles if role.name.lower() == self.role.lower()][0]
        qb = [member for member in ctx.guild.members if member.name.lower() == self.role.lower()][0]
        if qbr not in qb.roles:
            raise ValueError(f'Queuebot role ({self.role}) not assigned to queuebot ({qb.name})')

        # remove general channels if existing
        gt = discord.utils.get(ctx.guild.text_channels, name='general')
        if gt:
            await gt.delete()
        gt = discord.utils.get(ctx.guild.voice_channels, name='General')
        if gt:
            await gt.delete()

        # Extract permissions from config
        tutor_permission_obj = get_permissions('tutor_role', overwrite=False)
        meeting_permission_obj = get_permissions('meeting_role', overwrite=False)

        tr_ow_t = get_permissions('meeting_text_read')
        qbr_ow_t = get_permissions('meeting_text_read')
        mr_ow_t = get_permissions('member_meeting_text')
        er_ow_t = get_permissions('everyone_meeting_text')

        tr_ow_v = get_permissions('tutor_meeting_voice')
        qbr_ow_v = get_permissions('bot_meeting_voice')
        mr_ow_v = get_permissions('member_meeting_voice')
        er_ow_v = get_permissions('everyone_meeting_voice')

        er_ow_wt = get_permissions('welcome')
        er_ow_ch = get_permissions('chatter')
        er_ow_ad = get_permissions('everyone_admin')
        qbr_ow_ad = get_permissions('bot_admin')
        tr_ow_ad = get_permissions('tutor_admin')
        tr_ow_wr = get_permissions('tutor_waiting_room')
        er_ow_wr = get_permissions('everyone_waiting_room')

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
        for channel_name in config['channel_names'][:self.config['Nchannels']]:
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
            await wt.send(config['welcome_text'])
        if not discord.utils.get(ctx.guild.text_channels, name='chatter'):
            await ctx.guild.create_text_channel(name = 'chatter', overwrites={er:er_ow_ch}, category=tct)
        if not discord.utils.get(ctx.guild.text_channels, name='queue'):
            await ctx.guild.create_text_channel(name = 'queue', category=tct, slowmode_delay=15)
        for spam_channel in config['spam_channels']:
            if not discord.utils.get(ctx.guild.text_channels, name=spam_channel):
                await ctx.guild.create_text_channel(name = spam_channel, category=tct, slowmode_delay=5)
        for admin_channel in self.config['admin_channels']:
            if not discord.utils.get(ctx.guild.text_channels, name=admin_channel):
                await ctx.guild.create_text_channel(name = admin_channel, overwrites={er:er_ow_ad,qbr:qbr_ow_ad,tr:tr_ow_ad}, category=tct)
        if not discord.utils.get(ctx.guild.voice_channels, name=self.config['waiting_room']):
            await ctx.guild.create_voice_channel(name = self.config['waiting_room'], overwrites={er:er_ow_wr,tr:tr_ow_wr}, category=vct)

        await self.toggle(ctx)

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
            channel = discord.utils.get(ctx.guild.text_channels, name=self.config['queue_channel'])
            await channel.send(f'You are up **{member.mention}**! Please join channel **{member.roles[-1]}**.')
            self.queue.remove(self.queue[0])
        await ctx.message.delete()

    @is_approved()
    @commands.command(pass_context=True, name='bye')
    async def _bye(self, ctx):
        role = [s for s in ctx.guild.roles 
                if s.name.lower()==ctx.channel.name.lower()][0]
        waiting_room_obj = discord.utils.get(ctx.guild.voice_channels, 
                                             name=self.config['waiting_room'])
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
            if member.nick:
                await ctx.send(f'{member.nick} is up next')
            else:
                await ctx.send(f'{member.name} is up next')
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
        qchannel = discord.utils.get(ctx.guild.text_channels, name=self.config['queue_channel'])
        if ctx.channel != qchannel:
            await qchannel.send(f'Queue is now {state}')

#---------------------------------------------------------
# Bot Creation 
#--------------------------------------------------------
client = commands.Bot(command_prefix=config['queuebot']['prefix'])

@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(activity=discord.Game(name='Queuing Fun'))

client.add_cog(Queue(client))

if __name__ == "__main__":
    if config['queuebot']['token'] and "--noop" not in sys.argv:
        client.run(config['queuebot']['token'])
    elif "--noop" in sys.argv:
        from pprint import PrettyPrinter
        PrettyPrinter(indent=2).pprint(config)
