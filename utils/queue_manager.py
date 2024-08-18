import random

class QueueManager:
    def __init__(self):
        self.queues = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def add_to_queue(self, guild_id, song_info):
        self.get_queue(guild_id).append(song_info)

    def clear_queue(self, guild_id):
        if guild_id in self.queues:
            self.queues[guild_id].clear()

    def remove_from_queue(self, guild_id, index):
        queue = self.get_queue(guild_id)
        if 0 <= index < len(queue):
            return queue.pop(index)
        return None
    
    def remove_slice_from_queue(self, guild_id, amount):
        queue = self.get_queue(guild_id)
        if amount > 0 and amount <= len(queue):
            removed_tracks = queue[:amount]
            self.queues[guild_id] = queue[amount:]
            return removed_tracks
        return None

    def shuffle_queue(self, guild_id):
        queue = self.get_queue(guild_id)
        random.shuffle(queue)

    def move_track(self, guild_id, from_index, to_index):
        queue = self.get_queue(guild_id)
        if from_index < 1 or from_index > len(queue) or to_index < 1 or to_index > len(queue):
            return None
        else:
            song = queue.pop(from_index - 1)
            queue.insert(to_index - 1, song)
            return song.get('title')

# Instância global do QueueManager
queue_manager = QueueManager()