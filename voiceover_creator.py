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


def create_voiceover(post, filename):
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

    with open((filename + ".mp3"), "wb") as binary_file:
        binary_file.write(voiceover)


if __name__ == "__main__":
    post = {
        'title': 'God created the first Swiss and asked him:',
        'body': '"What do you want?" "Mountains," replied the Swiss.\n\nGod created mountains for the Swiss and asked him, "What else do you want?" "Cows," said the Swiss.\n\nGod created cows for the Swiss. The Swiss milked the cows, tasted the milk and asked, "Will you taste, dear God?" The Swiss filled a cup with milk and handed it to God. Dear God took the cup, drank it and said, "The milk is really quite good. What more do you want?"\n\n\"1.20 Swiss Franc.\"'
    }
    # example_text = "\n\nThis is some \n\n\n\ntext for\n a joke.\nIt is very funny.\n\n\n\n\nHaha laugh.\n\n"

    create_voiceover(post)
    # format_ssml(post['title'] + "\n" + post['body'])