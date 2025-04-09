DEEP_RESEARCH = """
The following headline and abstract is a trending news headline from the {source}.

Research all current news articles that provide information and context related to this topic.
Your job is to find multiple perspectives and expert options for an UNBIASED summary of the topic.

Focus specifically on obataining data that is factual, unbiased, and supported by multiple sources. This data can be
expert opinions, related events, statistical data, future implications. Give specific facts and evidence to support the evidence.

Your content should be a 1-2 paragraphs of dense, UNBIASED, summary of the entire topic and story.
    
Your results will be used by a downstream AI agent, so much sure to output the results and NOTHING ELSE but the results. 

<HEADLINE>{headline}</HEADLINE>
<ABSTRACT>{abstract}</ABSTRACT>
"""

SEARCH_ARTICLES = """

TODAY IS {date}
Here is the user's topic of interest: {category}
List {max_articles} articles that are related to this topic of interest that are recent and timely. They need to be real
and current news articles.

Just return the headline in the format below. Do not return any other text. Your 
results will be used by a downstream AI agent, so much sure to output the results and NOTHING ELSE but the results.

<HEADLINE_1>

</HEADLINE_1>

<HEADLINE_2>

</HEADLINE_2>

...
"""

COMPOSE_STORY = """

You are an AI agent that is an expert news anchor host. You are reporting on the following story headline: {headline}. 

Your job is to be as UNBIASED, ACCURATE, and DENSE AS POSSIBLE. You have the following information on this topic.

{research}

Use this information to compose a 5-sentence summary of the entire story. The first sentence should be a strong
introduction that gives a good overview of the story. You should present the story in an interesting, engaging, and coherent way.

Add natural breaks and new lines to make it easier to read at a first glance.

Your results will be used by a downstream AI agent, so much sure to output the results and NOTHING ELSE but the results.
"""

SELECT_DIVERSE_ARTICLES = """
Given the following list of {num_articles} article headlines and abstracts, select the top {num_select} articles that represent the widest diversity of topics within the general category of '{topic}'.

Focus on variety. Avoid selecting multiple articles that cover the exact same specific event or sub-topic unless they offer significantly different perspectives mentioned in the abstract.

Please return only the zero-based indices of the selected articles, separated by commas (e.g., "0,3,5,7,10,12,15,18"). Do not include any other text, explanation, or the headlines/abstracts themselves.

The user may enter a focus topic. If the following focus is NOT GENERAL, then choose topics that most closely align with the focus.
Otherwise proceed normally and proceed normally choosing diverse articles
{focus}

ARTICLES:
{article_list_text}

Selected Indices:
"""

SELECT_DIVERSE_X_POSTS = """
You are analyzing a list of {num_posts} posts from X (formerly Twitter) related to the news headline: "{headline}".

Your task is to select the top {num_select} posts that offer the most impactful insights or represent the widest spread of public opinion or reactions regarding this news topic. Prioritize posts that:
- Offer unique perspectives or information.
- Represent different sentiments (if applicable).
- Seem to have significant engagement or represent a common viewpoint.
- Are relevant and directly related to the headline.

Avoid selecting posts that are purely spam, repetitive, or offer no substance.

Please return only the zero-based indices of the selected posts, separated by commas (e.g., "0,2,5,8,11,14,17,19,22,25"). Do not include any other text, explanation, or the post content itself.

POSTS:
{post_list_text}

Selected Indices:
"""
FOLLOW_UP_PROMPT = """
You gave the user multiple news stories. However, they have now asked a quesiton about one of the stories. Please, to
the best of your ability, answer the following question using the information from the stories.
If you do not understand the information, do NOT make it up, just say I don't know. Keep your response to 2-3 sentences,
unless the question is extremely complex. Figure out which story the user is referring to from the question and abstracts given.

Your response will be parsed and used by a downstream AI agent. As a result DO NOT output anything but the response.

You have the following news stories
{news}

The user asked the following question:
{question}

"""

INSIGHTS_PROMPT = """
You have the following summary of a news story. Your job is to use this story to drive both takeways and trading insights.
That is, using this information, do the following
(1) Create a summary takeaway / trading insight that is one sentence
(2) Create one trade that will likely increase.
(3) Create one trade that will likely decrease.

UNDER NO CIRCUMSTANCE DO YOU OUTPUT ANY BACKTICKS, OR ANYTHING AROUND THE JSON.
OUTPUT JUST THE JSON. ANYTHING ELSE WILL BREAK THE JSON PARSER.

Your response will be parsed and used by a downstream AI agent. As a result DO NOT output anything but the following JSON format
for your response
{{
    "summary": "",
    "positive": {{
        "headline": "At most 3 words, typically a stock ticker, or trade description",
        "description": "Describe the positive trade in 2-3 sentences"
    }},
    "negative": {{
        "headline": "At most 3 words, typically a stock ticker, or trade description",
        "description": "Describe the negative trade in 2-3 sentences"
    }}
}}

Here is the attached summary
{summary}
"""