import boto3
from dotenv import load_dotenv
import os


def format_ssml(text, speed=100):
    '''
    Given a string and optional speed, format it using AWS Polly's SSML syntax.
    Speed must be in the range [20-200]%
    '''
    prefix = "<speak><prosody rate=\"{}%\">".format(speed)
    suffix = "</prosody></speak>"

    # Turn newlines into <break />, adding only one <break /> if there are multiple \n in a row
    characters = [*text]
    for i in range(len(characters) - 1, 0, -1):
        if characters[i] == characters[i-1] == '\n':
            del characters[i]

    ssml = prefix + ("".join(characters)).replace('\n', "<break />") + suffix

    return ssml


def create_voiceover(post):
    '''
    Uses the AWS Polly API to create a voiceover of a reddit post.
    '''
    load_dotenv()

    region = os.getenv('AWS_REGION')
    polly_access = os.getenv('POLLY_ACCESS')
    polly_secret = os.getenv('POLLY_SECRET')

    client = boto3.client(
        'polly', 
        region_name=region,
        aws_access_key_id=polly_access,
        aws_secret_access_key=polly_secret,
    )

    ssml = format_ssml(post['title']+"\n"+post['body'])

    response = client.synthesize_speech(
        Engine='neural',
        OutputFormat='mp3',
        SampleRate='24000',
        Text=ssml,
        TextType='ssml',
        VoiceId='Matthew'
    )

    voiceover = response['AudioStream'].read()

    with open("voiceover.mp3", "wb") as binary_file:
        binary_file.write(voiceover)


if __name__ == "__main__":
    post = {
        'title': 'Why did the chicken cross the road?',
        'body': 'To get to the other side.'
    }
    # example_text = "\n\nThis is some \n\n\n\ntext for\n a joke.\nIt is very funny.\n\n\n\n\nHaha laugh.\n\n"

    create_voiceover(post)