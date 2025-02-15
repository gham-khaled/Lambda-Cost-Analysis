/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */

import { useContext, useEffect, useState } from 'react'
import Header from '../partials/Header'
import Sidebar from '../partials/Sidebar'
import 'primereact/resources/themes/vela-green/theme.css'

import { Calendar } from 'primereact/calendar'
import { FloatLabel } from 'primereact/floatlabel'
import MultiSelect from '../components/MultiSelect'
import { RotatingLines } from 'react-loader-spinner'

import axios from 'axios'

import { architectureOptions, successMsgStyle } from '../data/optionsData'
import { InputText } from 'primereact/inputtext'
import AnalysisContext from '../contexts/AnalysisContext'
import { customToast } from '../utils/utils'
import { useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

const PROD_API_URL = window.PROD_URL_API

const Analysis = () => {
	const {
		startDate,
		setStartDate,
		endDate,
		setEndDate,
		setCurrentReportID,
		selectedRuntime,
		setSelectedRuntime,
		initialRuntime,
		setInitialRuntime,
		initialPackageOptions,
		setInitialPackageOptions,
		selectedPackageOptions,
		setSelectedPackageOptions,
		initialArchitectureOptions,
		setInitialArchitectureOptions,
		selectedArchitectureOptions,
		setSelectedArchitectureOptions,
		selectedFunctions,
		setSelectedFunctions,
	} = useContext(AnalysisContext)

	const columns = [
		{ Header: 'Function name', accessor: 'FunctionName' },
		{ Header: 'Runtime', accessor: 'Runtime' },
		{ Header: 'PackageType', accessor: 'PackageType' },
		{ Header: 'Architecture', accessor: 'Architectures' },
		{ Header: 'LastModified', accessor: 'LastModified' },
	]

	const [analysisID, setAnalysisID] = useState('')
	const { setAnalysisDetail } = useContext(AnalysisContext)

	const [loading, setLoading] = useState(false)
	const [isFetching, setIsFetching] = useState(false)
	const [maxAttemptsReached, setMaxAttemptsReached] = useState(false)
	const [lambdaFunctions, setLambdaFunctions] = useState([])

	const [isFiltered, setIsFiltered] = useState(false)

	const navigate = useNavigate()

	const handleFetchFunctions = async () => {
		setLoading(true)
		try {
			// API call to fetch lambda functions with parameters

			// const response = await axios.get(
			// 	'api/lambdaFunctions?selectedRuntime=$[selectedRuntime]',
			// 	{
			// 		params: new URLSearchParams({
			// 			selectedRuntime: isFiltered ? selectedRuntime : initialRuntime,
			// 			selectedPackageType: isFiltered
			// 				? selectedPackageOptions
			// 				: initialPackageOptions,
			// 			selectedArchitecture: isFiltered
			// 				? selectedArchitectureOptions
			// 				: initialArchitectureOptions,
			// 		}),
			// 	}
			// )

			// API call to fetch lambda functions without any parameters

			const response = await axios.get(`${PROD_API_URL}/lambdaFunctions`)
			const functions = response.data

			handleFilters(functions)
			setSelectedFunctions(functions)
			setLambdaFunctions(functions)

			// console.log('Lambda functions: ', functions)

			setLoading(false)
		} catch (error) {
			console.error('Error fetching lambda functions: ', error)
			setLoading(false)
		}
	}

	// Client side filter functions based on fetched data
	const handleFilters = (functions) => {
		if (!isFiltered) {
			// Only set the initial filters from the fetched data once
			const fetchedFilteredRuntime = [
				...new Set(functions.map((func) => func.Runtime)),
			]

			const fetchedFilteredPackageTypes = [
				...new Set(functions.map((func) => func.PackageType)),
			]

			const fetchedFilteredArchitectureOptions = [
				...new Set(functions.flatMap((func) => func.Architectures)),
			]

			setInitialRuntime(fetchedFilteredRuntime)
			setSelectedRuntime(fetchedFilteredRuntime)

			setInitialPackageOptions(fetchedFilteredPackageTypes)
			setSelectedPackageOptions(fetchedFilteredPackageTypes)

			setInitialArchitectureOptions(fetchedFilteredArchitectureOptions)
			setSelectedArchitectureOptions(fetchedFilteredArchitectureOptions)

			setIsFiltered(true) // Set the flag to true after the first filtering
		}
	}

	useEffect(() => {
		// Fetch lambda functions on component mount
		handleFetchFunctions()
	}, [])

	const handleLaunchAnalysis = async () => {
		customToast('Analysis launched successfully', '✅', successMsgStyle)

		const unixStartDate = new Date(startDate.setHours(0, 0, 0, 0)).toISOString()
		const unixEndDate = new Date(endDate.setHours(23, 59, 59, 999)).toISOString()

		const reportID = analysisID || Math.floor(Date.now() / 1000) // Use analysisID if provided, otherwise use timestamp
		localStorage.setItem('reportID', reportID.toString())

		setMaxAttemptsReached(false)
		setCurrentReportID(reportID)

		const payload = {
			lambda_functions_name: selectedFunctions.map(
				(lambdaFunction) => lambdaFunction['FunctionName']
			),
			report_id: reportID,
			start_date: unixStartDate,
			end_date: unixEndDate,
		}
		setIsFetching(true)
		try {
			const response = await axios.post(`${PROD_API_URL}/startExecution`, payload)
			// console.log(`Start Execution Response: ${response}`)
			// console.log(response)

			await getAnalysisDetail(reportID)
		} catch (error) {
			console.error('Error fetching lambda functions: ', error)
			setLoading(false)
		}
	}

	const errorMsgStyle = {
		fontSize: '12px',
		border: '0.4px solid #787474',
		borderRadius: '5px',
		background: '#253645',
		color: '#fff',
	}

	const getAnalysisDetail = async (reportID) => {
		try {
			const response = await fetchDataWithRetry(reportID)
			setAnalysisDetail(response.data)
			navigate(`/report/reportID=${reportID}`) // Navigate on success
		} catch (error) {
			console.error('Error fetching report details: ', error)
			// Display error message here
		} finally {
			// setLoading(false)
			setIsFetching(false)
		}
	}

	// Function to delay execution
	const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

	const fetchDataWithRetry = async (reportID, maxAttempts = 10) => {
		let attempts = 0

		while (attempts < maxAttempts) {
			// Retry fetching data 5 times b/c the API may not return the data immediately
			try {
				const response = await axios.get(
					`${PROD_API_URL}/report?reportID=${reportID}`
				)
				// console.log(`Report Detail Response: ${response}`)
				console.log(response)
				if (response.status === 200) {
					return response // Return response if successful
				}
				attempts++
				await delay(3000)
			} catch (error) {
				if (attempts === maxAttempts - 1) {
					customToast('Maximum attempts reached', '❌', errorMsgStyle)
					setMaxAttemptsReached(true)

					// console.error('Max attempts reached')
					throw error // Throw error on the last attempt
				}
				attempts++
				await delay(3000)
			}
		}
		throw new Error('Max attempts reached')
	}

	return (
		<div className='flex'>
			<Toaster />
			<Sidebar />
			<div className='bg-darkblue w-full h-screen overflow-y-scroll p-10 pt-0 space-y-6 '>
				<Header title='Analysis | New'></Header>
				<div className='col-span-12 lg:col-span-12 space-y-4 pt-8'>
					{lambdaFunctions.length !== 0 && (
						<>
							<div className='grid grid-cols-2 md:grid-cols-6  gap-x-6 gap-y-10 text-xs'>
								<FloatLabel>
									<MultiSelect
										options={initialRuntime}
										selectedValues={selectedRuntime}
										setSelectedValues={setSelectedRuntime}
										placeholder='Runtime'
										maxSelectedLabels={1}
										selectedItemsLabel={selectedRuntime[0] + ' ...'}
									/>
									<label htmlFor='runtime'>Runtime</label>
								</FloatLabel>

								<FloatLabel>
									<MultiSelect
										options={initialPackageOptions}
										selectedValues={selectedPackageOptions}
										setSelectedValues={setSelectedPackageOptions}
										placeholder='Package'
										maxSelectedLabels={1}
										selectedItemsLabel={selectedPackageOptions[0] + ' ...'}
									/>
									<label htmlFor='package_option'>Package</label>
								</FloatLabel>
								<FloatLabel>
									<MultiSelect
										options={initialArchitectureOptions}
										selectedValues={selectedArchitectureOptions}
										setSelectedValues={setSelectedArchitectureOptions}
										placeholder='Architecture'
										maxSelectedLabels={1}
										selectedItemsLabel={architectureOptions[0] + ' ...'}
									/>
									<label htmlFor='architecture_option'>Architecture</label>
								</FloatLabel>

								{/* Fetch Lambda function */}
								{/* <button
							className={`${!loading || (!loading && isFetching) ? 'bg-[#00A9817D] opacity-90 ' : 'bg-gray-500'} text-white text-xs p-2 rounded-md text-wrap`}
							onClick={handleFetchFunctions}
							disabled={loading || isFetching}
						>
							{loading ? 'Fetching Fns...' : 'Fetch Lambda Fns'}
						</button> */}
							</div>

							<div className='col-span-12 lg:col-span-12 space-y-4 pt-8'>
								<div className='grid grid-cols-2 md:grid-cols-6 text-[10px]  gap-x-6 gap-y-10'>
									<FloatLabel>
										<InputText
											id='analysis_id'
											value={analysisID}
											onChange={(e) => setAnalysisID(e.target.value)}
											className='bg-darkblueLight border-none text-white text-xs  py-2 px-6  rounded-md w-full'
										/>
										<label htmlFor='analysis_id'>Analysis ID (Optional)</label>
									</FloatLabel>
									<FloatLabel>
										<Calendar
											value={startDate}
											onChange={(e) => setStartDate(e.value)}
											showIcon
											showButtonBar
											className='bg-darkblueLight border-none text-white text-xs   rounded-md w-full'
											inputClassName='bg-darkblueLight text-white text-xs border-none px-2 py-2 rounded-md  '
										/>
										<label htmlFor='start_date'>Start Date</label>
									</FloatLabel>
									<FloatLabel>
										<Calendar
											value={endDate}
											onChange={(e) => {
												if (e.value > startDate) {
													setEndDate(e.value)
												}
											}}
											showIcon
											showButtonBar
											className='bg-darkblueLight border-none text-white text-xs   rounded-md w-full'
											inputClassName='bg-darkblueLight text-white text-xs border-none px-2 py-2  rounded-md'
										/>
										<label htmlFor='end_date'>End Date</label>
									</FloatLabel>

									<button
										className={`${!isFetching ? 'bg-lambdaPrimary' : 'bg-gray-500'} text-white text-xs py-1 rounded-md  `}
										onClick={() => {
											if (selectedFunctions.length === 0) {
												customToast(
													'Please Fetch lambda fns and select at least one  before launching the analysis.',
													'❌',
													errorMsgStyle
												)
											} else {
												handleLaunchAnalysis()
											}
										}}
										disabled={isFetching}
									>
										{isFetching ? 'Fetching...' : 'New Analysis'}
									</button>
								</div>
								{isFetching && (
									<div className='text-xs text-yellow-600 pt-4'>
										Please wait while we fetch the analysis details...
									</div>
								)}
								{maxAttemptsReached && (
									<div className='text-xs text-red-600 pt-4'>
										Oops! Maximum attempts reached. Please try again later.
									</div>
								)}
							</div>
						</>
					)}
					<div className='pt-8'>
						<DynamicTable
							columns={columns}
							data={lambdaFunctions}
							loading={loading}
						/>
					</div>
				</div>
			</div>
		</div>
	)
}

const DynamicTable = ({ columns, data, loading = false }) => {
	const {
		setSelectedFunctions,
		selectedRuntime,
		selectedArchitectureOptions,
		selectedPackageOptions,
	} = useContext(AnalysisContext)
	const [checkedItems, setCheckedItems] = useState({})

	useEffect(() => {
		// Initialize or reset checkedItems state when data changes
		const newCheckedItems = {}
		data.forEach((item, index) => {
			newCheckedItems[index] = true // Initially, all items are checked
		})
		setCheckedItems(newCheckedItems)
	}, [data])

	const handleSelectAll = (e) => {
		const newCheckedItems = { ...checkedItems }
		Object.keys(newCheckedItems).forEach((key) => {
			newCheckedItems[key] = e.target.checked
		})
		setCheckedItems(newCheckedItems)
		const selected = Object.keys(newCheckedItems)
			.filter((key) => newCheckedItems[key])
			.map((key) => data[key])
		setSelectedFunctions(selected)
	}

	const handleSelectItem = (index, isChecked) => {
		const newCheckedItems = { ...checkedItems, [index]: isChecked }
		setCheckedItems(newCheckedItems)
		const selected = Object.keys(newCheckedItems)
			.filter((key) => newCheckedItems[key])
			.map((key) => data[key])
		setSelectedFunctions(selected)
	}

	const allChecked = Object.values(checkedItems).every(Boolean)

	return (
		<>
			{data.length !== 0 ? (
				<div className='relative overflow-x-auto shadow-md sm:rounded-md'>
					<table className='w-full text-sm text-left rtl:text-right text-white border border-darkblueLight rounded-md'>
						<thead className='text-xs uppercase text-white bg-darkblueLight'>
							<tr>
								<th scope='col' className='px-6 py-3'>
									<input
										type='checkbox'
										checked={allChecked}
										onChange={handleSelectAll}
									/>
								</th>
								{columns.map((column) => (
									<th key={column.accessor} scope='col' className='px-6 py-3'>
										{column.Header}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{data
								.filter(
									(row) =>
										selectedRuntime.includes(row.Runtime) &&
										selectedPackageOptions.includes(row.PackageType) &&
										selectedArchitectureOptions.some(
											(architecture) => row.Architectures.includes(architecture)
											// .some method returns true if at least one element in the array satisfies the condition where Architectures is an array of strings
										)
								)

								.map((row, index) => {
									// Log the current row to the console
									// console.log(row.row)

									return (
										<tr
											key={index}
											className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer text-xs hover:bg-green-900/40`}
										>
											<td className='px-6 py-3'>
												<input
													type='checkbox'
													checked={checkedItems[index] || false}
													onChange={(e) => handleSelectItem(index, e.target.checked)}
												/>
											</td>
											{columns.map((column) => (
												<td key={column.accessor} className='px-6 py-3'>
													{column.Cell
														? column.Cell(row[column.accessor])
														: row[column.accessor]}
												</td>
											))}
										</tr>
									)
								})}
						</tbody>
					</table>
				</div>
			) : (
				<div className='text-gray-400 text-center flex justify-center items-center h-28 text-md mt-10'>
					{loading ? (
						<RotatingLines
							visible={true}
							height='40'
							width='40'
							color='darkblueLight'
							strokeWidth='5'
							animationDuration='1'
							ariaLabel='rotating-lines-loading'
							wrapperStyle={{}}
							wrapperClass=''
						/>
					) : (
						<>Data is not available</>
					)}
				</div>
			)}
		</>
	)
}

export default Analysis
