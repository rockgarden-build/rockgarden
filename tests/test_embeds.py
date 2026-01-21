"""Tests for media embed processing."""

from rockgarden.obsidian.embeds import (
    embed_to_html,
    is_audio_embed,
    is_image_embed,
    is_media_embed,
    is_pdf_embed,
    is_video_embed,
    parse_embed,
    process_media_embeds,
)


class TestParseEmbed:
    """Tests for parse_embed function."""

    def test_basic_image(self):
        """Parse basic image embed."""
        result = parse_embed("image.png", None)
        assert result.target == "image.png"
        assert result.alt_text is None
        assert result.width is None
        assert result.height is None

    def test_with_alt_text(self):
        """Parse image with alt text."""
        result = parse_embed("image.png", "my alt text")
        assert result.target == "image.png"
        assert result.alt_text == "my alt text"
        assert result.width is None
        assert result.height is None

    def test_with_width_only(self):
        """Parse image with width dimension."""
        result = parse_embed("image.png", "100")
        assert result.target == "image.png"
        assert result.alt_text is None
        assert result.width == 100
        assert result.height is None

    def test_with_width_and_height(self):
        """Parse image with width and height dimensions."""
        result = parse_embed("image.png", "100x200")
        assert result.target == "image.png"
        assert result.alt_text is None
        assert result.width == 100
        assert result.height == 200

    def test_with_path(self):
        """Parse image with folder path."""
        result = parse_embed("folder/image.png", None)
        assert result.target == "folder/image.png"
        assert result.filename == "image.png"

    def test_whitespace_stripped(self):
        """Whitespace in target and params is stripped."""
        result = parse_embed("  image.png  ", "  alt text  ")
        assert result.target == "image.png"
        assert result.alt_text == "alt text"


class TestIsImageEmbed:
    """Tests for is_image_embed function."""

    def test_png_is_image(self):
        assert is_image_embed("image.png") is True

    def test_jpg_is_image(self):
        assert is_image_embed("photo.jpg") is True

    def test_jpeg_is_image(self):
        assert is_image_embed("photo.jpeg") is True

    def test_gif_is_image(self):
        assert is_image_embed("animation.gif") is True

    def test_svg_is_image(self):
        assert is_image_embed("vector.svg") is True

    def test_webp_is_image(self):
        assert is_image_embed("modern.webp") is True

    def test_uppercase_extension(self):
        assert is_image_embed("image.PNG") is True

    def test_md_is_not_image(self):
        assert is_image_embed("note.md") is False

    def test_no_extension(self):
        assert is_image_embed("noextension") is False

    def test_with_path(self):
        assert is_image_embed("folder/image.png") is True


class TestEmbedToHtml:
    """Tests for embed_to_html function."""

    def test_basic_image(self):
        """Basic image produces img tag with src and alt."""
        embed = parse_embed("image.png", None)
        result = embed_to_html(embed, "/image.png")
        assert result == '<img src="/image.png" alt="image.png">'

    def test_with_alt_text(self):
        """Custom alt text is used."""
        embed = parse_embed("image.png", "my description")
        result = embed_to_html(embed, "/image.png")
        assert result == '<img src="/image.png" alt="my description">'

    def test_with_width(self):
        """Width attribute is added."""
        embed = parse_embed("image.png", "100")
        result = embed_to_html(embed, "/image.png")
        assert result == '<img src="/image.png" alt="image.png" width="100">'

    def test_with_dimensions(self):
        """Width and height attributes are added."""
        embed = parse_embed("image.png", "100x200")
        result = embed_to_html(embed, "/image.png")
        expected = '<img src="/image.png" alt="image.png" width="100" height="200">'
        assert result == expected

    def test_with_path(self):
        """Path in src, filename in alt."""
        embed = parse_embed("folder/image.png", None)
        result = embed_to_html(embed, "/folder/image.png")
        assert result == '<img src="/folder/image.png" alt="image.png">'

    def test_html_escaping(self):
        """Special characters are escaped."""
        embed = parse_embed("image.png", 'alt with "quotes" & <brackets>')
        result = embed_to_html(embed, "/path/to/image.png")
        assert 'alt="alt with &quot;quotes&quot; &amp; &lt;brackets&gt;"' in result


class TestProcessImageEmbeds:
    """Tests for process_media_embeds function."""

    def _mock_resolver(self, target):
        """Simple resolver that returns the target as URL and path."""
        return f"/{target}", target

    def test_basic_embed(self):
        """Basic image embed is converted."""
        content = "![[image.png]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == '<img src="/image.png" alt="image.png">'
        assert images == {"image.png"}

    def test_embed_with_alt_text(self):
        """Embed with alt text is converted."""
        content = "![[image.png|my alt text]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == '<img src="/image.png" alt="my alt text">'
        assert images == {"image.png"}

    def test_embed_with_width(self):
        """Embed with width is converted."""
        content = "![[image.png|100]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == '<img src="/image.png" alt="image.png" width="100">'

    def test_embed_with_dimensions(self):
        """Embed with dimensions is converted."""
        content = "![[image.png|100x200]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        expected = '<img src="/image.png" alt="image.png" width="100" height="200">'
        assert result == expected

    def test_embed_with_path(self):
        """Embed with folder path is converted."""
        content = "![[folder/image.png]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == '<img src="/folder/image.png" alt="image.png">'
        assert images == {"folder/image.png"}

    def test_multiple_embeds(self):
        """Multiple embeds are all converted."""
        content = "![[one.png]] and ![[two.jpg]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert '<img src="/one.png"' in result
        assert '<img src="/two.jpg"' in result
        assert images == {"one.png", "two.jpg"}

    def test_non_image_embed_preserved(self):
        """Non-image embeds (e.g., note transclusion) are preserved."""
        content = "![[note.md]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == "![[note.md]]"
        assert images == set()

    def test_unresolved_embed_preserved(self):
        """Unresolved image embeds are preserved."""

        def resolver(target):
            return None

        content = "![[missing.png]]"
        result, images = process_media_embeds(content, resolver)
        assert result == "![[missing.png]]"
        assert images == set()


class TestCodeBlockPreservation:
    """Tests for code block preservation."""

    def _mock_resolver(self, target):
        return f"/{target}", target

    def test_embed_in_fenced_code_block(self):
        """Embeds in fenced code blocks are not transformed."""
        content = "```\n![[image.png]]\n```"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == "```\n![[image.png]]\n```"
        assert images == set()

    def test_embed_in_inline_code(self):
        """Embeds in inline code are not transformed."""
        content = "Use `![[image.png]]` syntax."
        result, images = process_media_embeds(content, self._mock_resolver)
        assert result == "Use `![[image.png]]` syntax."
        assert images == set()

    def test_embed_outside_code_block(self):
        """Embeds outside code blocks are still transformed."""
        content = "```\ncode\n```\n\n![[image.png]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert "```\ncode\n```" in result
        assert '<img src="/image.png"' in result
        assert images == {"image.png"}

    def test_mixed_content(self):
        """Mixed code and regular content is handled correctly."""
        content = "![[one.png]] `![[two.png]]` ![[three.png]]"
        result, images = process_media_embeds(content, self._mock_resolver)
        assert '<img src="/one.png"' in result
        assert "`![[two.png]]`" in result
        assert '<img src="/three.png"' in result
        assert images == {"one.png", "three.png"}


class TestIsAudioEmbed:
    """Tests for is_audio_embed function."""

    def test_mp3_is_audio(self):
        assert is_audio_embed("song.mp3") is True

    def test_wav_is_audio(self):
        assert is_audio_embed("sound.wav") is True

    def test_m4a_is_audio(self):
        assert is_audio_embed("podcast.m4a") is True

    def test_ogg_is_audio(self):
        assert is_audio_embed("music.ogg") is True

    def test_flac_is_audio(self):
        assert is_audio_embed("lossless.flac") is True

    def test_png_is_not_audio(self):
        assert is_audio_embed("image.png") is False


class TestIsVideoEmbed:
    """Tests for is_video_embed function."""

    def test_mp4_is_video(self):
        assert is_video_embed("movie.mp4") is True

    def test_webm_is_video(self):
        assert is_video_embed("clip.webm") is True

    def test_mov_is_video(self):
        assert is_video_embed("video.mov") is True

    def test_mkv_is_video(self):
        assert is_video_embed("film.mkv") is True

    def test_png_is_not_video(self):
        assert is_video_embed("image.png") is False


class TestIsPdfEmbed:
    """Tests for is_pdf_embed function."""

    def test_pdf_is_pdf(self):
        assert is_pdf_embed("document.pdf") is True

    def test_uppercase_pdf(self):
        assert is_pdf_embed("document.PDF") is True

    def test_png_is_not_pdf(self):
        assert is_pdf_embed("image.png") is False


class TestIsMediaEmbed:
    """Tests for is_media_embed function."""

    def test_image_is_media(self):
        assert is_media_embed("image.png") is True

    def test_audio_is_media(self):
        assert is_media_embed("song.mp3") is True

    def test_video_is_media(self):
        assert is_media_embed("movie.mp4") is True

    def test_pdf_is_media(self):
        assert is_media_embed("doc.pdf") is True

    def test_markdown_is_not_media(self):
        assert is_media_embed("note.md") is False


class TestAudioEmbedToHtml:
    """Tests for audio embed HTML generation."""

    def _mock_resolver(self, target):
        return f"/{target}", target

    def test_audio_embed(self):
        """Audio embed produces audio tag with controls."""
        content = "![[song.mp3]]"
        result, media = process_media_embeds(content, self._mock_resolver)
        assert result == '<audio controls src="/song.mp3"></audio>'
        assert media == {"song.mp3"}


class TestVideoEmbedToHtml:
    """Tests for video embed HTML generation."""

    def _mock_resolver(self, target):
        return f"/{target}", target

    def test_video_embed(self):
        """Video embed produces video tag with controls."""
        content = "![[movie.mp4]]"
        result, media = process_media_embeds(content, self._mock_resolver)
        assert result == '<video src="/movie.mp4" controls></video>'
        assert media == {"movie.mp4"}

    def test_video_with_dimensions(self):
        """Video embed with dimensions has width/height."""
        content = "![[movie.mp4|640x480]]"
        result, media = process_media_embeds(content, self._mock_resolver)
        assert 'width="640"' in result
        assert 'height="480"' in result


class TestPdfEmbedToHtml:
    """Tests for PDF embed HTML generation."""

    def _mock_resolver(self, target):
        return f"/{target}", target

    def test_pdf_embed(self):
        """PDF embed produces iframe."""
        content = "![[document.pdf]]"
        result, media = process_media_embeds(content, self._mock_resolver)
        assert '<iframe src="/document.pdf"' in result
        assert media == {"document.pdf"}

    def test_pdf_with_dimensions(self):
        """PDF embed with dimensions has custom width/height."""
        content = "![[document.pdf|800x600]]"
        result, media = process_media_embeds(content, self._mock_resolver)
        assert 'width="800px"' in result
        assert 'height="600px"' in result
