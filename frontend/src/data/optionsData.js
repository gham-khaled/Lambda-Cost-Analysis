const runtime = [
	'nodejs20.x',
	'nodejs18.x',
	'nodejs16.x',
	'python3.12',
	'python3.11',
	'python3.10',
	'python3.9',
	'python3.8',
	'java21',
	'java17',
	'java11',
	'java8.al2',
	'dotnet8',
	'dotnet7',
	'dotnet6',
	'ruby3.3',
	'ruby3.2',
	'provided.al2023',
	'provided.al2',
	'nodejs14.x',
	'ruby2.7',
	'provided',
	'go1.x',
	'java8',
]

const packageOptions = ['Zip', 'Image']

const architectureOptions = ['x86_64', 'arm64']

const statistics = [
	{
		title: 'Memory Cost',
		icon: 'BiSolidCategoryAlt',
		query: '',
	},
	{
		title: 'Invocation Cost',
		icon: 'IoIosCube',
		query: '',
	},
	{
		title: 'Total Cost',
		icon: 'AiOutlineShop',
		query: '',
	},
	{
		title: 'Potential Savings',
		icon: 'AiOutlineUser',
		query: '',
	},
	{
		title: 'Avg.Max Memory Used',
		icon: 'BiSolidCategoryAlt',
		query: '',
	},
	{
		title: 'Abg. Provisioned Memory',
		icon: 'IoIosCube',
		query: '',
	},
	{
		title: 'Avg Duration / Invocation',
		icon: 'AiOutlineShop',
		query: '',
	},
]

const errorMsgStyle = {
	fontSize: '12px',
	border: '0.4px solid #787474',
	borderRadius: '5px',
	background: '#253645',
	color: '#fff',
}

const successMsgStyle = {
	fontSize: '12px',
	border: '0.4px solid #787474',
	borderRadius: '5px',
	background: '#253645',
	color: '#fff',
}

const summaryColumns = [
	{ label: 'Report ID', key: 'reportID' },
	{ label: 'Status', key: 'status' },
	{ label: 'Start Date', key: 'startDate' },
	{ label: 'End Date', key: 'endDate' },
	{ label: 'Total Cost', key: 'totalCost' },
	{ label: 'Optimal Total Cost', key: 'optimalTotalCost' },
	{ label: 'Potential Savings', key: 'potentialSavings' },

	{ label: 'Memory Cost', key: 'MemoryCost' },
	{ label: 'Invocation Cost', key: 'InvocationCost' },
	{ label: 'Timeout Invocations', key: 'timeoutInvocations' },
	{ label: 'Memory Exceeded Invocation', key: 'memoryExceededInvocation' },
	// { label: 'allDurationInSeconds', key: 'allDurationInSeconds' },

	{ label: 'Avg Cost Per Invocation', key: 'avgCostPerInvocation' },
	{ label: 'Avg Max Memory Used MB', key: 'avgMaxMemoryUsedMB' },
	{ label: 'Avg Over Provisioned MB', key: 'avgOverProvisionedMB' },
	{ label: 'Avg Provisioned Memory MB', key: 'avgProvisionedMemoryMB' },
	{
		label: 'Avg Duration Per Invocation',
		key: 'avgDurationPerInvocation',
	},



]

const reportDetailsColumns = [
	{ key: 'functionName', label: 'Function Name' },
	{ key: 'architecture', label: 'Architecture' },
	{ key: 'runtime', label: 'Runtime' },
	{ key: 'provisionedMemoryMB', label: 'Provisioned Memory (MB)' },
	{ key: 'maxMemoryUsedMB', label: 'Max Memory Used (MB)' },
	{ key: 'overProvisionedMB', label: 'Over Provisioned (MB)' },
	{ key: 'optimalMemory', label: 'Optimal Memory (MB)' },
	{ key: 'totalCost', label: 'Total Cost' },
	{ key: 'potentialSavings', label: 'Potential Savings' },

	{ key: 'MemoryCost', label: 'Memory Cost' },
	{ key: 'InvocationCost', label: 'Invocation Cost' },

	{ key: 'allDurationInSeconds', label: 'Duration (s)' },
	{ key: 'avgCostPerInvocation', label: 'Avg Cost/Invocation' },
	{ key: 'avgDurationPerInvocation', label: 'Avg Duration/Invocation' },



	{ key: 'memoryExceededInvocation', label: 'Memory Exceeded Invocation' },
	{ key: 'timeoutInvocations', label: 'Timeout Invocations' },
]


export {
	runtime,
	packageOptions,
	architectureOptions,
	statistics,
	errorMsgStyle,
	successMsgStyle,
	summaryColumns,
	reportDetailsColumns,
}