from crewai import Agent, Task, Crew,Process
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
from codeagent.current_item import CurrentItem
import json
# Define tools (assuming some tools are already created, replace with actual tools if needed)
# from your_tool_library import SpecificTool1, SpecificTool2, SpecificTool3
import os

os.environ['OPENAI_API_KEY'] = "enter key here before running"
#os.environ["OPENAI_API_KEY"] = "NA"

class UnoplatAgent:
    def __init__(self):
        self.md_spec_data = self.read_md_unoplat_spec('codebase_overview_spec.md')
        self.json_data = self.read_json_file('codebase_summary.json')
        self.item_reader_tool = CurrentItem(self.json_data)
        
        # self.llm = ChatOpenAI(
        #     model="phi3:14b-medium-4k-instruct-q8_0",
        #     base_url="http://localhost:11434/v1"
        # )
        self.llm = ChatOpenAI(
            model='gpt-4o',
            temperature=0,
            top_p=0.3
        )
        self.agent1 = Agent(
            role='Data Engineer',
            goal="""Goal is to fetch data item from tool.""",
            backstory="""An experienced engineer who knows how to fetch data from the tool. 
            Post successful fetch format the data properly as per markdown syntax.
            The only reason if data is not returned is that we are done with entire data and there is no more data to process. When that happens it is time to inform the manager that prepare the final summary using Senior Markdown Technical Documentation Specialist in markdown with to shutdown and exit.""",
            memory=False,
            verbose=True,
            llm=self.llm,
            cache=False,
            allow_delegation=False,
            tools=[self.item_reader_tool]
        )
        # Create agents with memory enabled and specific goals and backstories
        self.agent2 = Agent(
            role='Software Engineer',
            goal=""" First you will understand each and everything in the class metadata and the spec.
             Second you will convert the shared class metadata into component level information based on responsibility. Strictly do not include more than that like avoid methods,fields etc.
             .Pro tip: Keep the component name as package name if package name is available.""",
            backstory="""An experienced engineer skilled in synthesizing complex data into actionable insights. You work
            for Unoplat a platform company which is stringent in following specifications.""",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.agent3 = Agent(
            role='Senior Software Engineer',
            goal="""the goal is to understand the refine overall codebase summary based on all per class summaries received up until now.""",
            backstory="You are a senior software engineer with over 10 years of experience in writing codebase summary and are very good at capturing flows in terms of mermaid flow graph",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

        self.agent4 = Agent(
            role='Senior Markdown Technical Documentation Specialist',
            goal="Analyze the evolving summary for accuracy and insights based on all available classes' metadata and include flow/interactions within the codebases between classes.",
            backstory="You work for Unoplat. A detail-oriented tech doc specialist who specializes in tech documentation and focuses on triggers and flow within the codebase.",
            memory=True,
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        self.manager_agent = Agent(
            role='Tech Doc Manager',
            goal="""Ultimate goal is codebase summary which captures flow between classes and their triggers based on user shared metadata per class. 
            Goal is to go over each data item at a time from a list of items. Each class metadata is fetched from Data Engineer at one time and then converted into right markdown spec by
            Software Engineer and then current item summary is added to overall codebase summary again based  by Senior Software Engineer.THen you repeat the flow again until there are no elements. Post error from data fetch tool do a final
            testing of markdown spec with help of Senior Markdown Technical Documentation Specialist.Then you can exit.""",
            backstory="You are a manager who knows how to manage the crew and ensure that the crew is working on the tasks in the right order and that the data is being passed between the agents correctly. Do not waste any more time than required.",
            memory=True,
            verbose=True,
            llm=self.llm
        )
      # Define tasks
        self.task1 = Task(
            description='Fetch data from tool to get class summary one at a time. No arguments are needed to pass to the tool. Tool would tell if we have reached the end. ',
            expected_output='Nicely formatted and spaced markdown. If error is encountered during the process it is time to exit.',
            tool_choice=[self.item_reader_tool]
        )
        self.task2 = Task(
            description=f"""Now the goal is to output the content into markdown based on specification {self.md_spec_data}.""",
            expected_output='Current summary of codebase in markdown spec.'
            
        )

        self.task3 = Task(
            description='Look at overall summary that we have and current summary for item that we received just now and then review and refine overall summary for accuracy and completeness according to the unoplat markdown spec based on {unoplat_markdown_spec}.',
            expected_output='Overall codebase Summary in markdown for all components which includes- Refined summary with corrections and keep it concise. Remember it is summary so focus is on components and its internal flows and external flows. Strictly do not include more than that.',
            
        )

        self.task4 = Task(
            description='Check the markdown syntax in content received which contains codebase summary .',
            expected_output='Final report in markdown incorporating all refinements in markdown following common mark specification.',
            output_file="unoplat_tech_doc.md",
            tools=[]
        )

        # Assemble the crew without a manager
        self.unoplat_crew = Crew(
            agents=[self.agent1, self.agent2, self.agent3,self.agent4],
            tasks=[self.task1, self.task2, self.task3, self.task4],
            process=Process.hierarchical,
            manager_agent=self.manager_agent,
            verbose=2,
            cache=False
        )

    def read_json_file(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def read_md_unoplat_spec(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Function to kick off the crew tasks iteratively
    def run_crew(self):
        
        self.unoplat_crew.kickoff ()  # Process the current item

        print("Crew tasks completed. Check outputs for details.")
# Example usage




