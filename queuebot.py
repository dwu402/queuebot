import discord
from discord.ext import commands

prefix = "!"
client = commands.Bot(command_prefix=prefix)

approved_roles = ['Tutor']
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
            await channel.send(f'You are up **{member.mention}**! Have fun!')
            self.queue.remove(self.queue[0])
        await ctx.message.delete()

    @is_approved()
    @commands.command(pass_context=True, name='bye')
    async def _bye(self, ctx):
        role = [s for s in ctx.guild.roles 
                if s.name.lower()==ctx.channel.name.lower()][0]
        waiting_room = discord.utils.get(ctx.guild.voice_channels, name=waiting_room)
        for member in role.members:
            await member.remove_roles(role)
            await member.move_to(waiting_room)

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

client.add_cog(Queue(client))

if __name__ == "__main__":
    client.run('YOUR_TOKEN_HERE')
