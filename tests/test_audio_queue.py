import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bot.utils.audio_queue import AudioQueue, AudioItem


class TestAudioQueue:
    @pytest.fixture
    def audio_queue(self):
        aq = AudioQueue()
        aq._log = MagicMock()  # Mock the logger
        return aq

    def test_get_queue_new(self, audio_queue):
        queue = audio_queue.get_queue(123)
        assert isinstance(queue, asyncio.Queue)
        assert 123 in audio_queue._queues

    def test_get_queue_existing(self, audio_queue):
        queue1 = audio_queue.get_queue(123)
        queue2 = audio_queue.get_queue(123)
        assert queue1 is queue2

    @pytest.mark.asyncio
    async def test_add_to_queue_new_task(self, audio_queue):
        voice_state = MagicMock()
        voice_state.channel.guild.id = 123
        voice_state.channel.guild.voice_client = None
        voice_state.channel.connect = AsyncMock()

        item = AudioItem(b'audio', voice_state, 'text', 123)

        with patch.object(audio_queue, '_play_loop', new_callable=AsyncMock) as mock_play:
            await audio_queue.add_to_queue(item)
            assert 123 in audio_queue._play_tasks
            mock_play.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_add_to_queue_existing_task_done(self, audio_queue):
        voice_state = MagicMock()
        voice_state.channel.guild.id = 123

        item = AudioItem(b'audio', voice_state, 'text', 123)

        # Simulate existing task that's done
        mock_task = MagicMock()
        mock_task.done.return_value = True
        audio_queue._play_tasks[123] = mock_task

        with patch.object(audio_queue, '_play_loop', new_callable=AsyncMock) as mock_play:
            await audio_queue.add_to_queue(item)
            # Should create new task
            assert audio_queue._play_tasks[123] is not mock_task
            mock_play.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_add_to_queue_existing_task_running(self, audio_queue):
        voice_state = MagicMock()
        voice_state.channel.guild.id = 123

        item = AudioItem(b'audio', voice_state, 'text', 123)

        # Simulate existing task that's running
        mock_task = MagicMock()
        mock_task.done.return_value = False
        audio_queue._play_tasks[123] = mock_task

        with patch.object(audio_queue, '_play_loop', new_callable=AsyncMock) as mock_play:
            await audio_queue.add_to_queue(item)
            # Should not create new task
            assert audio_queue._play_tasks[123] is mock_task
            mock_play.assert_not_called()

    def test_clear(self, audio_queue):
        audio_queue._queues[123] = asyncio.Queue()
        mock_task = MagicMock()
        audio_queue._play_tasks[123] = mock_task

        audio_queue.clear(123)

        assert isinstance(audio_queue._queues[123], asyncio.Queue)
        mock_task.cancel.assert_called_once()

    def test_clear_nonexistent(self, audio_queue):
        # Should not raise error
        audio_queue.clear(999)
