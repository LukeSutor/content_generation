from dotenv import load_dotenv
import boto3
import os


def format_ssml(text, speed=100):
    '''
    Given a string and optional speed, format it using AWS Polly's SSML syntax.
    Speed must be in the range [20-200]%
    '''
    prefix = "<speak><prosody rate=\"{}%\">".format(speed)
    suffix = "</prosody></speak>"

    # Exchange reserved characters for their ssml escaoe characters
    text = text.replace("&", "&amp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("'", "&apos;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # Turn newlines into <break />, adding only one <break /> if there are multiple \n in a row
    characters = [*text]
    for i in range(len(characters) - 1, 0, -1):
        if characters[i] == characters[i-1] == '\n':
            del characters[i]

    ssml = ("".join(characters)).replace('\n', "<break />")

    # Add beginning and ending parts
    ssml = prefix + ssml + suffix

    return ssml


def create_voiceover(post, filename, comment=None):
    '''
    Uses the AWS Polly API to create a voiceover of a reddit post.
    '''
    load_dotenv()
    region = os.getenv('AWS_REGION')
    polly_access = os.getenv('POLLY_ACCESS')
    polly_secret = os.getenv('POLLY_SECRET')
    save_path = os.getenv('SAVE_PATH')

    client = boto3.client(
        'polly', 
        region_name=region,
        aws_access_key_id=polly_access,
        aws_secret_access_key=polly_secret,
    )

    # Get the total word count to set the speed for the voiceover
    wordcount = len(post['title'].split()) + len(post['body'].split())
    if comment is not None:
        wordcount += len(comment['body'].split())
    # This function keeps the speed at 105% until you get over 100 words
    # then gradually speeds up the talking until you get to 200% at 480 words
    speed = min(int(max(105, (wordcount + 320) * 0.25)), 200)

    ssml = format_ssml(post['title']+"\n"+post['body'], speed=speed)

    response = client.synthesize_speech(
        Engine='neural',
        OutputFormat='mp3',
        SampleRate='24000',
        Text=ssml,
        TextType='ssml',
        VoiceId='Matthew'
    )

    voiceover = response['AudioStream'].read()

    with open(os.path.join(save_path, filename + ".mp3"), "wb") as binary_file:
        binary_file.write(voiceover)

    # Do the same for the comment
    if comment is not None:
        ssml = format_ssml(comment['body'], speed=speed)

        response = client.synthesize_speech(
        Engine='neural',
        OutputFormat='mp3',
        SampleRate='24000',
        Text=ssml,
        TextType='ssml',
        VoiceId='Matthew'
        )
        
        voiceover = response['AudioStream'].read()

        with open(os.path.join(save_path, filename + "_comment" + ".mp3"), "wb") as binary_file:
            binary_file.write(voiceover)


if __name__ == "__main__":
    post = {
        'title': 'God created the first Swiss and asked him:',
        'body': 'This is the body of the post.'
    }

    comment = {
        'body': 'This is the body of the comment.'
    }
    # example_text = "\n\nThis is some \n\n\n\ntext for\n a joke.\nIt is very funny.\n\n\n\n\nHaha laugh.\n\n"

    create_voiceover(post, "test", comment=comment)
    # format_ssml(post['title'] + "\n" + post['body'])