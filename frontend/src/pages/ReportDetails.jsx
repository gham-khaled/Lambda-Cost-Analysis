/* eslint-disable react/prop-types */
import Header from '../partials/Header'
import Sidebar from '../partials/Sidebar'

import {useParams} from 'react-router-dom'
import StatisticsList from '../components/StatisticsList'
import React, {useContext, useEffect, useState} from 'react'
import axios from 'axios'
import {ThreeDots} from 'react-loader-spinner'
import {Toaster} from 'react-hot-toast'
import {customToast} from '../utils/utils'
import {errorMsgStyle} from '../data/optionsData'
import AnalysisContext from '../contexts/AnalysisContext'
import {reportDetailsColumns as columns} from '../data/optionsData'
import {Chart} from 'primereact/chart'
import {Tooltip} from 'react-tooltip'
import {Chart as ChartJS} from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'

const PROD_API_URL = window.PROD_URL_API

const ReportDetails = () => {
    const {reportID} = useParams()
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

    const {
        analysis,
        setAnalysis,
        // analysisDetail,
        summary,
        setSummary,
        downloadURL,
        setDownloadURL,
        status,
        setStatus,
        setAnalysisDetail,
    } = useContext(AnalysisContext)

    const [loading, setLoading] = useState(false)
    //
    // useEffect(() => {
    //     setSummary(analysisDetail.summary)
    //     setStatus(analysisDetail.status)
    //     setAnalysis(analysisDetail.analysis)
    // }, [
    //     analysisDetail,
    //     reportID,
    //     status,
    //     summary,
    //     analysis,
    //     setAnalysis,
    //     setSummary,
    //     setStatus,
    // ])
    const downloadFile = () => {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = downloadURL;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    useEffect(() => {
        setAnalysis([])
        setAnalysisDetail({})
        const fetchData = async () => {
            setLoading(true)
            try {
                const response = await axios.get(`${PROD_API_URL}/report?${reportID}`)
                if (response.status === 200) {
                    setStatus(response.data.summary.status)
                    setSummary(response.data.summary)
                    if (response.data.summary.status === 'Failed') {
                        customToast('The Analysis Encountered an Error', '❌', errorMsgStyle)
                        setLoading(false)
                    } else if (response.data.summary.status === 'Running') {
                        // console.log('Fetching Data Again')
                        await delay(3000)
                        return await fetchData()
                    } else {
                        setAnalysis(response.data.analysis)
                        setAnalysisDetail(response.data)
                        setDownloadURL(response.data.url)
                        setLoading(false)
                    }

                    return response // Return response if successful
                }
            } catch (error) {
                customToast('Server is not responding', '❌', errorMsgStyle)
                throw error // Throw error on the last attempt
            }
        }

        fetchData()
    }, [reportID, setAnalysis, setSummary, setStatus])

    const reportNumber = reportID.split('=')

    return (
        <div className='flex'>
            <Toaster/>
            <Sidebar/>
            <div className='bg-darkblue w-full h-screen overflow-y-scroll p-10 pt-0 space-y-6 '>
                <Header title='Analysis | Dashboard'></Header>

                <div className='flex flex-col  gap-y-4 lg:gap-y-4 pb-6'>
                    <div
                        className=' text-base flex flex-row  font-semibold text-third-dark items-center   rounded-md  '>
                        <p>Analysis ID : </p>
                        <p className='text-white/70 text-sm ml-4'>{reportNumber[1]}</p>
                    </div>
                    {status === 'Completed' && (
                        <div className='text-sm flex flex-row font-semibold text-lambdaPrimary rounded-md justify-between'>
                            <div className='flex items-center'>
                                <p className='hidden lg:flex'>Analysis Date:</p>
                                <p className='text-white/70 text-sm lg:ml-4'>
                                    {new Date(summary.startDate).toDateString()} - {new Date(summary.endDate).toDateString()}
                                </p>
                            </div>
                            <button onClick={downloadFile} className='ml-auto  bg-lambdaPrimary text-white px-4 py-2 rounded'>
                                Download CSV
                            </button>
                        </div>
                    )}

                </div>

                {status === 'Completed' && analysis.length > 0 ? (
                    <>
                        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
                            <CostBreakdownChart analysis={analysis}/>
                            <CostSummaryBoxes summary={summary} analysis={analysis}/>
                        </div>
                    </>
                ) : status === 'Running' ? (
                    <div className='flex flex-col justify-center items-center h-64 gap-4'>
                        <ThreeDots
                            visible={true}
                            height='60'
                            width='60'
                            color='#eab308'
                            radius='9'
                            ariaLabel='three-dots-loading'
                            wrapperStyle={{}}
                            wrapperClass=''
                        />
                        <p className='text-base text-yellow-500 font-medium'>
                            Report is still processing...
                        </p>
                        <p className='text-sm text-gray-400'>
                            This page will automatically update when complete
                        </p>
                    </div>
                ) : (
                    status === 'Failed' && (
                        <div className='flex flex-col justify-center items-center h-64 gap-4'>
                            <div className='text-center'>
                                <p className='text-base text-red-500 font-medium'>Report generation failed</p>
                                <p className='text-sm text-gray-400 mt-2'>Please try running the analysis again</p>
                                {summary && summary.errorCode && (
                                    <div className='mt-4 p-3 bg-red-900/20 border border-red-500 rounded text-sm text-gray-300'>
                                        <p className='font-semibold'>Error Code: {summary.errorCode}</p>
                                        <p className='mt-1'>{summary.errorMessage}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )
                )}
                {loading && (
                    <div className='flex justify-center items-center mt-10'>
                        <ThreeDots
                            visible={true}
                            height='40'
                            width='40'
                            color='#4fa94d'
                            radius='9'
                            ariaLabel='three-dots-loading'
                            wrapperStyle={{}}
                            wrapperClass=''
                        />
                    </div>
                )}

                {status === 'Completed' && (
                    <div className='pt-4'>
                        {' '}
                        <DynamicTable data={analysis}/>{' '}
                    </div>
                )}
            </div>
        </div>
    )
}

const DynamicTable = ({data}) => {
    const [sortConfig, setSortConfig] = useState({
        key: null,
        direction: 'ascending',
    })

    const [showColumnSelector, setShowColumnSelector] = useState(false)
    const columnSelectorRef = React.useRef(null)

    // Define default visible columns (main ones)
    const defaultVisibleColumns = [
        'functionName',
        'countInvocations',
        'provisionedMemoryMB',
        'maxMemoryUsedMB',
        'optimalMemory',
        'totalCost',
        'potentialSavings',
        'timeoutInvocations',
        'logSizeGB'
    ]

    const [visibleColumns, setVisibleColumns] = useState(defaultVisibleColumns)

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (columnSelectorRef.current && !columnSelectorRef.current.contains(event.target)) {
                setShowColumnSelector(false)
            }
        }

        if (showColumnSelector) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [showColumnSelector])

    const sortedData = React.useMemo(() => {
        let sortableItems = [...data]
        if (sortConfig !== null) {
            sortableItems.sort((a, b) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? -1 : 1
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? 1 : -1
                }
                return 0
            })
        }
        return sortableItems
    }, [data, sortConfig])

    const requestSort = (key) => {
        let direction = 'ascending'
        if (sortConfig.key === key && sortConfig.direction === 'ascending') {
            direction = 'descending'
        }
        setSortConfig({key, direction})
    }

    const toggleColumn = (columnKey) => {
        if (visibleColumns.includes(columnKey)) {
            setVisibleColumns(visibleColumns.filter(key => key !== columnKey))
        } else {
            setVisibleColumns([...visibleColumns, columnKey])
        }
    }

    const visibleColumnsData = columns.filter(col => visibleColumns.includes(col.key))

    return (
        <>
            {data.length !== 0 ? (
                <div className='space-y-4'>
                    {/* Column Selector Button */}
                    <div className='flex justify-end'>
                        <div className='relative' ref={columnSelectorRef}>
                            <button
                                onClick={() => setShowColumnSelector(!showColumnSelector)}
                                className='bg-lambdaPrimary hover:bg-yellow-600 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors'
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" />
                                </svg>
                                Show/Hide Columns
                            </button>

                            {/* Column Selector Dropdown */}
                            {showColumnSelector && (
                                <div className='absolute right-0 mt-2 w-64 bg-darkblueMedium border border-darkblueLight rounded-md shadow-lg z-50 max-h-96 overflow-y-scroll'>
                                    <div className='p-3 border-b border-darkblueLight'>
                                        <div className='flex justify-between items-center'>
                                            <h3 className='text-sm font-semibold text-white'>Select Columns</h3>
                                            <button
                                                onClick={() => setVisibleColumns(columns.map(c => c.key))}
                                                className='text-xs text-lambdaPrimary hover:text-yellow-600'
                                            >
                                                Show All
                                            </button>
                                        </div>
                                    </div>
                                    <div className='p-2'>
                                        {columns.map((column) => (
                                            <label
                                                key={column.key}
                                                className='flex items-center px-3 py-2 hover:bg-darkblue rounded cursor-pointer'
                                            >
                                                <input
                                                    type='checkbox'
                                                    checked={visibleColumns.includes(column.key)}
                                                    onChange={() => toggleColumn(column.key)}
                                                    className='mr-3 w-4 h-4 text-lambdaPrimary bg-darkblue border-gray-600 rounded focus:ring-lambdaPrimary'
                                                />
                                                <span className='text-sm text-white'>{column.label}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className='relative overflow-x-auto shadow-md sm:rounded-md'>
                        <table
                            className='w-full text-sm text-left rtl:text-right text-white border border-darkblueLight rounded-md'>
                        <thead className='text-xs uppercase text-white bg-darkblueLight py-2'>
                        <tr className='px-6 py-3 cursor-pointer '>
                            {visibleColumnsData.map((column) => (
                                <th
                                    key={column.key}
                                    scope='col'
                                    className='px-6 py-3  hover:text-third-dark transition-all duration-300 ease-in-out'
                                    onClick={() => requestSort(column.key)}
                                    data-tooltip-id={column.tooltip ? `tooltip-${column.key}` : undefined}
                                    data-tooltip-content={column.tooltip}
                                >
                                    {column.label}
                                    {column.tooltip && <span className='ml-1 text-gray-400'>ℹ️</span>}
                                </th>
                            ))}
                        </tr>
                        </thead>
                        <tbody>
                        {sortedData.map((row, index) => (
                            <tr
                                key={index}
                                className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer text-xs hover:bg-green-900/40${row.timeoutInvocations > 0 ? 'text-red-500' : ''} ${row.provisionedMemoryMB > row.optimalMemory * 2 ? 'text-yellow-500' : ''}`}
                            >
                                {visibleColumnsData.map((column) => (
                                    <td key={column.key} className='px-6 py-3'>
                                        {row[column.key]}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        </tbody>
                    </table>
                    {visibleColumnsData.filter(c => c.tooltip).map((column) => (
                        <Tooltip
                            key={column.key}
                            id={`tooltip-${column.key}`}
                            place="top"
                            style={{
                                backgroundColor: '#1E293B',
                                color: '#CBD5E1',
                                fontSize: '12px',
                                maxWidth: '300px',
                                zIndex: 9999
                            }}
                        />
                    ))}
                    </div>
                </div>
            ) : (
                <div className='text-gray-400 text-center flex justify-center items-center  text-md mt-10'>
                    Data is not available
                </div>
            )}
        </>
    )
}

const CostBreakdownChart = ({analysis}) => {
    const [chartData, setChartData] = useState({})
    const [chartOptions, setChartOptions] = useState({})

    useEffect(() => {
        // Register the datalabels plugin
        ChartJS.register(ChartDataLabels)
    }, [])

    useEffect(() => {
        // Calculate total costs for each category
        const totalMemoryCost = analysis.reduce((sum, item) => sum + parseFloat(item.MemoryCost || 0), 0)
        const totalInvocationCost = analysis.reduce((sum, item) => sum + parseFloat(item.InvocationCost || 0), 0)
        const totalStorageCost = analysis.reduce((sum, item) => sum + parseFloat(item.StorageCost || 0), 0)
        const totalLogIngestionCost = analysis.reduce((sum, item) => sum + parseFloat(item.logIngestionCost || 0), 0)
        const totalLogStorageCost = analysis.reduce((sum, item) => sum + parseFloat(item.logStorageCost || 0), 0)
        const totalAnalysisCost = analysis.reduce((sum, item) => sum + parseFloat(item.analysisCost || 0), 0)

        // Combine log costs
        const totalLogsCost = totalLogIngestionCost + totalLogStorageCost + totalAnalysisCost

        const data = {
            labels: ['Memory', 'Invocation', 'Storage', 'Logs'],
            datasets: [
                {
                    data: [
                        totalMemoryCost.toFixed(4),
                        totalInvocationCost.toFixed(4),
                        totalStorageCost.toFixed(4),
                        totalLogsCost.toFixed(4)
                    ],
                    backgroundColor: [
                        '#3B82F6', // Blue for Memory
                        '#10B981', // Green for Invocation
                        '#F59E0B', // Amber for Storage
                        '#8B5CF6'  // Purple for Logs
                    ],
                    borderColor: '#1E293B',
                    borderWidth: 2
                }
            ]
        }

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#CBD5E1',
                        font: {
                            size: 14
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || ''
                            const value = context.parsed || 0
                            const total = context.dataset.data.reduce((a, b) => parseFloat(a) + parseFloat(b), 0)
                            const percentage = ((value / total) * 100).toFixed(2)
                            return `${label}: $${value} (${percentage}%)`
                        }
                    }
                },
                datalabels: {
                    display: false
                }
            }
        }

        setChartData(data)
        setChartOptions(options)
    }, [analysis])

    return (
        <div className='bg-darkblueMedium p-6 rounded-lg shadow-md'>
            <h2 className='text-xl font-semibold text-white mb-4'>Cost Breakdown by Category</h2>
            <div className='h-96'>
                <Chart type='pie' data={chartData} options={chartOptions} />
            </div>
        </div>
    )
}

const CostSummaryBoxes = ({summary, analysis}) => {
    // Calculate total invocations from analysis data
    const totalInvocations = analysis.reduce((sum, item) => sum + parseFloat(item.countInvocations || 0), 0)

    // Calculate total log size from analysis data
    const totalLogSize = analysis.reduce((sum, item) => sum + parseFloat(item.logSizeGB || 0), 0)

    // Calculate total analysis cost from analysis data
    const totalAnalysisCost = analysis.reduce((sum, item) => sum + parseFloat(item.analysisCost || 0), 0)

    const summaryData = [
        {
            title: 'Total Cost',
            value: `$${parseFloat(summary.totalCost || 0).toFixed(4)}`,
            icon: '💰',
            color: 'text-green-400',
            tooltip: 'Total cost including memory, invocation, storage, and log costs'
        },
        {
            title: 'Potential Savings',
            value: `$${parseFloat(summary.potentialSavings || 0).toFixed(4)}`,
            icon: '💎',
            color: 'text-blue-400',
            tooltip: 'Potential cost savings if you optimize memory allocation for all functions'
        },
        {
            title: 'Total Invocations',
            value: Math.round(totalInvocations).toLocaleString(),
            icon: '🔄',
            color: 'text-purple-400',
            tooltip: 'Total number of Lambda function invocations across all functions'
        },
        {
            title: 'Total Logs Size',
            value: `${totalLogSize.toFixed(4)} GB`,
            icon: '📊',
            color: 'text-amber-400',
            tooltip: 'Total size of CloudWatch logs generated by all functions'
        },
        {
            title: 'Analysis Cost',
            value: `$${totalAnalysisCost.toFixed(6)}`,
            icon: '🔍',
            color: 'text-cyan-400',
            tooltip: 'Total cost of analyzing CloudWatch Logs for this report'
        }
    ]

    return (
        <div className='bg-darkblueMedium p-6 rounded-lg shadow-md'>
            <h2 className='text-xl font-semibold text-white mb-4'>Key Metrics</h2>
            <div className='space-y-4'>
                {summaryData.map((item, index) => (
                    <div
                        key={index}
                        className='bg-darkblue p-4 rounded-lg border border-darkblueLight'
                        data-tooltip-id={`summary-tooltip-${index}`}
                        data-tooltip-content={item.tooltip}
                    >
                        <div className='flex items-center justify-between'>
                            <div className='flex items-center gap-3'>
                                <span className='text-2xl'>{item.icon}</span>
                                <span className='text-sm text-gray-400'>{item.title}</span>
                                <span className='text-xs text-gray-500'>ℹ️</span>
                            </div>
                            <span className={`text-lg font-semibold ${item.color}`}>
                                {item.value}
                            </span>
                        </div>
                        <Tooltip
                            id={`summary-tooltip-${index}`}
                            place="left"
                            style={{
                                backgroundColor: '#1E293B',
                                color: '#CBD5E1',
                                fontSize: '12px',
                                maxWidth: '300px',
                                zIndex: 9999
                            }}
                        />
                    </div>
                ))}
            </div>
        </div>
    )
}

export default ReportDetails
